"""Checks every evidence link in the curated data and heals dead ones.

A link that answers 404/410 on two consecutive runs is swapped for its closest
Internet Archive snapshot. Links that answer 401/403/429 are 'unverifiable' (many
government sites block automated checks), and links that time out or fail at the
network level are 'unreachable' (Russian and some Chinese government sites drop
foreign traffic); both are left alone, since the page itself is usually fine.
"""
import json
from concurrent.futures import ThreadPoolExecutor

from common import CURATED, FetchError, get_json, http_get, q, read_json

NAME = "links"
TITLE = "Evidence link health"
EVERY_DAYS = 7
SOURCE_URL = "https://archive.org/help/wayback_api.php"

DEAD = {404, 410}
BLOCKED = {401, 403, 405, 406, 429, 451}


def all_urls():
    urls = set()
    for name in ("sources", "people", "projects"):
        for item in read_json(CURATED / f"{name}.json", []):
            if item.get("url"):
                urls.add(item["url"])
    for ch in (read_json(CURATED / "channels.json", {}) or {}).values():
        for link in ch.get("links", []):
            if link.get("url"):
                urls.add(link["url"])
    return sorted(urls)


def check(url):
    try:
        return _check(url)
    except Exception as e:  # noqa: BLE001 - one odd URL must never sink the whole check
        return "error", None


def _check(url):
    for method in ("HEAD", "GET"):
        try:
            http_get(url, method=method, timeout=25, retries=1, backoff=2)
            return "ok", None
        except FetchError as e:
            if e.status in BLOCKED:
                return "unverifiable", e.status
            if e.status in DEAD:
                return "dead", e.status
            if method == "GET":
                return ("unreachable" if e.status is None else "error"), e.status
    return "error", None


def wayback(url):
    try:
        data = get_json(f"https://archive.org/wayback/available?url={q(url)}", retries=2)
        snap = (data.get("archived_snapshots") or {}).get("closest") or {}
        if snap.get("available") and str(snap.get("status", "200")).startswith("2"):
            return snap.get("url", "").replace("http://", "https://", 1)
    except (FetchError, json.JSONDecodeError):
        pass
    return None


def collect(prev):
    prev = prev or {}
    prev_status = prev.get("status", {})
    healed = dict(prev.get("healed", {}))
    urls = all_urls()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(urls, pool.map(check, urls)))
    status = {}
    for url, (state, code) in results.items():
        streak = (prev_status.get(url, {}).get("dead_streak", 0) + 1) if state == "dead" else 0
        status[url] = {"state": state, "code": code, "dead_streak": streak}
        if state == "ok" and url in healed:
            healed.pop(url)  # the original came back; stop pointing at the archive
        elif streak >= 2 and url not in healed:
            snap = wayback(url)
            if snap:
                healed[url] = snap
    counts = {}
    for s in status.values():
        counts[s["state"]] = counts.get(s["state"], 0) + 1
    return {"status": status, "healed": healed, "counts": counts, "checked": len(urls)}


def validate(payload, prev):
    c = payload.get("counts", {})
    n = payload.get("checked", 0) or 1
    if c.get("error", 0) + c.get("dead", 0) + c.get("unreachable", 0) > 0.6 * n:
        # More than 60% failing at once is almost certainly our network, not the web.
        return [f"{c} — looks like a runner network problem, keeping previous results"]
    return []
