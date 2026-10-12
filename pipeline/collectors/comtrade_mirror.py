"""Annual goods trade between the three, reported by both sides (UN Comtrade).

Russia stopped reporting in 2022, so China-Russia trade is read from China's
side. US-China is read from both sides; the gap between them is the 'mirror gap'.
"""
import time

from common import FetchError, get_json, today, try_variants

NAME = "comtrade"
TITLE = "Mirror trade statistics (UN Comtrade)"
EVERY_DAYS = 30
SOURCE_URL = "https://comtradeplus.un.org"

M49 = {"CN": 156, "US": 842, "RU": 643}
# (reporter, partner, flow) — X = exports, M = imports
FLOWS = [
    ("CN", "RU", "X"), ("CN", "RU", "M"),
    ("CN", "US", "X"), ("CN", "US", "M"),
    ("US", "CN", "X"), ("US", "CN", "M"),
    ("US", "RU", "X"), ("US", "RU", "M"),
]


def _value(reporter, partner, flow, year):
    base = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
    url = (f"{base}?reporterCode={M49[reporter]}&period={year}&partnerCode={M49[partner]}"
           f"&cmdCode=TOTAL&flowCode={flow}")
    _, data = try_variants([
        ("preview", lambda: get_json(url, retries=5, backoff=3)),
        ("preview-customs", lambda: get_json(url + "&customsCode=C00&motCode=0", retries=3, backoff=3)),
    ])
    vals = [r.get("primaryValue") for r in data.get("data", []) or [] if r.get("primaryValue") is not None]
    if not vals:
        return None
    return float(max(vals))  # one TOTAL row expected; max guards against duplicate partner rows


def collect(prev):
    years = [today().year - i for i in (1, 2, 3, 4)]
    rows = []
    for rep, par, flow in FLOWS:
        for y in years:
            try:
                v = _value(rep, par, flow, y)
            except (FetchError, RuntimeError):
                v = None
            if v is not None:
                rows.append({"reporter": rep, "partner": par, "flow": flow, "year": y, "usd": v})
            time.sleep(1.2)  # stay well under the public preview's rate limit
    return {"rows": rows, "years_tried": years}


def validate(payload, prev):
    rows = payload.get("rows", [])
    problems = []
    cn_ru = [r for r in rows if r["reporter"] == "CN" and r["partner"] == "RU" and r["flow"] == "X"]
    if not cn_ru:
        problems.append("no China->Russia export rows returned")
    elif max(r["usd"] for r in cn_ru) < 1e10:
        problems.append("China->Russia exports implausibly low")
    if len(rows) < 8:
        problems.append(f"only {len(rows)} flow-years returned")
    return problems
