"""Shared helpers for the atlas pipeline (display name: ATLAS_NAME below).

Standard library only, on purpose: nothing to pip-install means nothing that
can break when a third-party package releases a new version.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CURATED = DATA / "curated"
LIVE = DATA / "live"

# The product's display name. Change it here and nowhere else: build.py puts it into the page
# (title, heading, meta tags) and notify.py into alert issues and emails. Internal identifiers
# (repo name, Pages URL, user agent, localStorage keys) deliberately keep their old names.
ATLAS_NAME = "World Signal Atlas"

USER_AGENT = "TriadSignalAtlas/1.0 (+https://github.com/datazen123/triad-signal-atlas)"

# Statuses worth retrying: rate limits and server-side hiccups.
RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504, 520, 522, 524}


class FetchError(Exception):
    def __init__(self, url: str, msg: str, status: int | None = None):
        super().__init__(f"{msg} <{url}>")
        self.url = url
        self.status = status


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date()


def parse_iso(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_json(path: Path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    tmp.replace(path)  # atomic: a crash never leaves a half-written file


def _retry_after(headers) -> float | None:
    val = headers.get("Retry-After") if headers else None
    if not val:
        return None
    try:
        return min(float(val), 120.0)
    except ValueError:
        try:
            when = email.utils.parsedate_to_datetime(val)
            return max(0.0, min(120.0, (when - dt.datetime.now(when.tzinfo)).total_seconds()))
        except (TypeError, ValueError):
            return None


# Tests swap this out to serve fixtures instead of touching the network.
_transport = None


def set_transport(fn) -> None:
    global _transport
    _transport = fn


def http_get(url: str, *, timeout: float = 45, retries: int = 4, backoff: float = 2.0,
             headers: dict | None = None, method: str = "GET") -> bytes:
    """GET with exponential backoff + jitter, honouring Retry-After."""
    if _transport is not None:
        return _transport(url, method=method)
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    last: Exception | None = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last = FetchError(url, f"HTTP {e.code}", e.code)
            if e.code not in RETRY_STATUS or attempt == retries:
                raise last from None
            wait = _retry_after(e.headers) or backoff ** (attempt + 1)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last = FetchError(url, f"network: {getattr(e, 'reason', e)}")
            if attempt == retries:
                raise last from None
            wait = backoff ** (attempt + 1)
        time.sleep(wait + random.uniform(0, 1))
    raise last or FetchError(url, "unknown failure")


def get_json(url: str, **kw):
    raw = http_get(url, headers={"Accept": "application/json"}, **kw)
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise FetchError(url, f"bad JSON: {e}") from None


def try_variants(variants):
    """Run (label, callable) pairs in order and return (label, result) of the first
    that succeeds. This is the first self-healing layer: when an upstream API
    changes its syntax, an alternative spelling often still works."""
    errors = []
    for label, fn in variants:
        try:
            return label, fn()
        except Exception as e:  # noqa: BLE001 - we want every failure recorded
            errors.append(f"{label}: {e}")
    raise RuntimeError("all variants failed -> " + " | ".join(errors))


def q(s: str) -> str:
    return urllib.parse.quote(s, safe="")
