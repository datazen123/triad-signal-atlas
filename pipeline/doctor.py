"""Runs the collectors that are due, isolates failures, and records health.

Self-healing layers, cheapest first (none of them call an AI model):
  1. Retries with exponential backoff (common.http_get).
  2. Alternative endpoint spellings per collector (common.try_variants).
  3. Validation against plausibility rules and the last good result; a result
     that fails is quarantined as 'suspect' instead of overwriting good data.
  4. Last-known-good data stays on the page, labelled with its age.
  5. Circuit breaker: after 3 straight failures a collector backs off to weekly
     attempts so a dead upstream is not hammered daily.
  6. Dead evidence links are swapped for Internet Archive snapshots (links collector).

Usage: python pipeline/doctor.py [--force] [--only NAME ...]
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import collectors  # noqa: E402
from common import DATA, LIVE, now_iso, parse_iso, read_json, write_json  # noqa: E402

HEALTH = DATA / "health.json"
BREAKER_AFTER = 3
BREAKER_DAYS = 7
ALERT_AFTER = 2  # consecutive failures before a human is told (avoids flapping alerts)


def due(entry: dict, every: int, now: dt.datetime) -> bool:
    last_try = parse_iso(entry.get("last_attempt"))
    if last_try is None:
        return True
    if entry.get("consecutive_failures", 0) >= BREAKER_AFTER:
        every = max(every, BREAKER_DAYS)
    elif entry.get("status") in ("fail", "suspect"):
        every = 1  # retry daily until it recovers or the breaker trips
    return now - last_try >= dt.timedelta(days=every) - dt.timedelta(hours=2)


def run_one(mod, entry: dict) -> dict:
    path = LIVE / f"{mod.NAME}.json"
    prev_doc = read_json(path)
    prev = prev_doc.get("payload") if prev_doc else None
    entry = dict(entry)
    entry["last_attempt"] = now_iso()
    started = dt.datetime.now(dt.timezone.utc)
    try:
        payload = mod.collect(prev)
        problems = mod.validate(payload, prev)
    except Exception as e:  # noqa: BLE001
        entry.update(status="fail", error=f"{type(e).__name__}: {e}"[:600],
                     trace=traceback.format_exc()[-1500:],
                     consecutive_failures=entry.get("consecutive_failures", 0) + 1)
        return entry
    entry["seconds"] = round((dt.datetime.now(dt.timezone.utc) - started).total_seconds(), 1)
    if problems:
        entry.update(status="suspect", error="; ".join(problems)[:600], trace=None,
                     consecutive_failures=entry.get("consecutive_failures", 0) + 1)
        write_json(LIVE / "quarantine" / f"{mod.NAME}.json", {"collected_at": now_iso(), "problems": problems, "payload": payload})
        return entry
    write_json(path, {"name": mod.NAME, "title": mod.TITLE, "source_url": mod.SOURCE_URL,
                      "collected_at": now_iso(), "payload": payload})
    entry.update(status="ok", error=None, trace=None, consecutive_failures=0, last_success=now_iso())
    return entry


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="run every collector now")
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args(argv)

    health = read_json(HEALTH, {}) or {}
    entries = health.get("collectors", {})
    now = dt.datetime.now(dt.timezone.utc)

    for mod in collectors.ALL:
        if args.only and mod.NAME not in args.only:
            continue
        entry = entries.get(mod.NAME, {})
        entry.update(title=mod.TITLE, every_days=mod.EVERY_DAYS, source_url=mod.SOURCE_URL)
        if not (args.force or args.only or due(entry, mod.EVERY_DAYS, now)):
            entry.setdefault("status", "pending")
            entries[mod.NAME] = entry
            print(f"[skip] {mod.NAME}: not due")
            continue
        print(f"[run ] {mod.NAME} ...", flush=True)
        entry = run_one(mod, entry)
        entries[mod.NAME] = entry
        print(f"[{entry['status']:>4}] {mod.NAME} {entry.get('error') or ''}")

    # Staleness: data older than 3x its cadence is flagged even if nothing 'failed'.
    for name, e in entries.items():
        last = parse_iso(e.get("last_success"))
        e["stale"] = bool(last and now - last > dt.timedelta(days=3 * e.get("every_days", 7) + 1))

    alerts = [
        {"collector": n, "status": e.get("status"), "error": e.get("error"),
         "consecutive_failures": e.get("consecutive_failures", 0), "stale": e.get("stale")}
        for n, e in sorted(entries.items())
        if e.get("consecutive_failures", 0) >= ALERT_AFTER or e.get("stale")
    ]
    write_json(HEALTH, {"last_run": now_iso(), "collectors": entries, "alerts": alerts})
    print(f"health written: {len(alerts)} alert(s)")
    return 0  # collector failures never block the site build; notify.py raises them


if __name__ == "__main__":
    sys.exit(main())
