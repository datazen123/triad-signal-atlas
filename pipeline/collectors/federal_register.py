"""US export-control actions naming China or Russia, per year (Federal Register API).

Counts Commerce Department (BIS) documents that mention the Entity List
together with each country. A legal-record signal of technology restriction.
"""
from common import get_json, q, try_variants

NAME = "fedreg"
TITLE = "US Entity List actions (Federal Register)"
EVERY_DAYS = 3
SOURCE_URL = "https://www.federalregister.gov/developers/documentation/api/v1"

COUNTRIES = {"CN": "China", "RU": "Russia"}


def _yearly(term: str) -> dict:
    base = "https://www.federalregister.gov/api/v1/documents/facets/yearly"
    url_a = f"{base}?conditions[term]={q(term)}&conditions[agencies][]=industry-and-security-bureau"
    url_b = f"{base}?conditions%5Bterm%5D={q(term)}&conditions%5Bagencies%5D%5B%5D=industry-and-security-bureau"
    _, data = try_variants([("brackets", lambda: get_json(url_a)), ("encoded", lambda: get_json(url_b))])
    out = {}
    for key, val in (data or {}).items():
        year = str(key)[:4]
        if year.isdigit() and isinstance(val, dict):
            out[year] = int(val.get("count", 0))
    return dict(sorted(out.items()))


def collect(prev):
    series = {code: _yearly(f'"entity list" {name}') for code, name in COUNTRIES.items()}
    return {"series": series, "query": '"entity list" + country, agency = BIS'}


def validate(payload, prev):
    problems = []
    for code, s in payload.get("series", {}).items():
        if len(s) < 5 or sum(s.values()) < 20:
            problems.append(f"{code} series implausibly small ({sum(s.values())} docs)")
    return problems
