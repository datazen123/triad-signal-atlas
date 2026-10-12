"""Active satellites and yearly launches by owner (CelesTrak SATCAT).

Owner codes follow CelesTrak: US, PRC, CIS (Russia/USSR), IND, JPN, UK, ESA, and
European national codes, which are summed into EU. 'ISS' objects are jointly owned.
"""
import csv
import io

from common import http_get, today, try_variants

NAME = "satcat"
TITLE = "Satellites in orbit (CelesTrak SATCAT)"
EVERY_DAYS = 7
SOURCE_URL = "https://celestrak.org/satcat/search.php"

OWNER_TO_POWER = {
    "US": "US", "PRC": "CN", "CIS": "RU", "IND": "IN", "JPN": "JP", "UK": "UK",
    "ESA": "EU", "FR": "EU", "GER": "EU", "IT": "EU", "SPN": "EU", "EUME": "EU", "EUTE": "EU",
    "NETH": "EU", "SWED": "EU", "POL": "EU", "FIN": "EU", "LUXE": "EU", "SES": "EU", "ISS": "JOINT",
}
ACTIVE = set("+PBSX")


def collect(prev):
    _, raw = try_variants([
        ("pub-csv", lambda: http_get("https://celestrak.org/pub/satcat.csv", timeout=120)),
        ("query-csv", lambda: http_get("https://celestrak.org/satcat/records.php?GROUP=active&FORMAT=csv", timeout=120)),
    ])
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8", "replace")))
    active, launches = {}, {}
    first = today().year - 10
    for row in reader:
        power = OWNER_TO_POWER.get((row.get("OWNER") or "").strip())
        if not power:
            continue
        is_payload = (row.get("OBJECT_TYPE") or "PAY").strip() == "PAY"
        if is_payload and (row.get("OPS_STATUS_CODE") or "").strip() in ACTIVE and not (row.get("DECAY_DATE") or "").strip():
            active[power] = active.get(power, 0) + 1
        y = (row.get("LAUNCH_DATE") or "")[:4]
        if is_payload and y.isdigit() and int(y) >= first:
            launches.setdefault(power, {}).setdefault(y, 0)
            launches[power][y] += 1
    return {"active_payloads": active, "payloads_launched": {k: dict(sorted(v.items())) for k, v in launches.items()}}


def validate(payload, prev):
    a = payload.get("active_payloads", {})
    problems = []
    if a.get("US", 0) < 1000:
        problems.append(f"US active payloads implausibly low ({a.get('US')})")
    if a.get("CN", 0) < 100:
        problems.append("China active payloads implausibly low")
    return problems
