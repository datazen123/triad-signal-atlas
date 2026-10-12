"""Active satellites and yearly launches by owner (CelesTrak SATCAT).

Owner codes follow CelesTrak (https://celestrak.org/satcat/sources.php): US, PRC,
CIS (Russia/USSR), IND/ISRO, JPN, UK, and the EU member states plus European
bodies (ESA, ESRO, EUMETSAT, EUTELSAT, SES and the France/Germany and France/Italy
joint codes), which are summed into EU. 'ISS' objects are jointly owned.
"""
import csv
import io

from common import http_get, today, try_variants

NAME = "satcat"
TITLE = "Satellites in orbit (CelesTrak SATCAT)"
EVERY_DAYS = 7
SOURCE_URL = "https://celestrak.org/satcat/search.php"

EU_OWNERS = {
    "ASRA", "BEL", "BUL", "HRV", "CZCH", "DEN", "EST", "FIN", "FR", "GER", "GREC", "HUN", "IRL",
    "IT", "LTU", "LUXE", "NETH", "POL", "POR", "ROM", "SVK", "SVN", "SPN", "SWED",
    "ESA", "ESRO", "EUME", "EUTE", "SES", "FGER", "FRIT",
}
OWNER_TO_POWER = {
    "US": "US", "PRC": "CN", "CIS": "RU", "IND": "IN", "ISRO": "IN", "JPN": "JP", "UK": "UK",
    "ISS": "JOINT", **{c: "EU" for c in EU_OWNERS},
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
