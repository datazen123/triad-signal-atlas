"""Co-authored research papers between each pair of powers, per year (OpenAlex).

A paper counts for a pair when its author list includes institutions in both.
This is raw cooperation data that keeps flowing even when politics sour.
"""
import os
from itertools import combinations

from common import get_json, today, try_variants

NAME = "openalex"
TITLE = "Research co-authorship (OpenAlex)"
EVERY_DAYS = 7
SOURCE_URL = "https://openalex.org"

# ISO codes OpenAlex uses. The EU is approximated by its largest research systems.
CODES = {
    "US": "US", "CN": "CN", "RU": "RU", "UK": "GB", "IN": "IN", "JP": "JP",
    "EU": "DE|FR|IT|ES|NL|SE|BE|AT|PL|DK|FI|IE|PT|CZ|GR",
}
FIRST_YEAR = 2000


def _url(field: str, codes: list[str], joiner: str) -> str:
    last = today().year
    parts = [f"{field}:{c}" for c in codes] + [f"publication_year:{FIRST_YEAR}-{last}"]
    url = ("https://api.openalex.org/works?filter=" + joiner.join(parts)
           + "&group_by=publication_year&per-page=200")
    mail = os.environ.get("CONTACT_EMAIL")
    return url + (f"&mailto={mail}" if mail else "")


def _series(codes: list[str]) -> dict:
    variants = []
    for field in ("authorships.institutions.country_code", "institutions.country_code"):
        for joiner in (",", "+"):
            variants.append((f"{field}{joiner}", lambda f=field, j=joiner: get_json(_url(f, codes, j))))
    _, data = try_variants(variants)
    out = {}
    for g in data.get("group_by", []):
        try:
            out[str(int(g["key"]))] = int(g["count"])
        except (KeyError, ValueError, TypeError):
            continue
    return dict(sorted(out.items()))


def collect(prev):
    pairs = {}
    for a, b in combinations(CODES, 2):
        pairs[f"{a}-{b}"] = _series([CODES[a], CODES[b]])
    totals = {k: _series([v]) for k, v in CODES.items()}
    return {"pairs": pairs, "totals": totals, "first_year": FIRST_YEAR,
            "note": "EU approximated by 15 member states' institutions."}


def validate(payload, prev):
    problems = []
    pairs = payload.get("pairs", {})
    if len(pairs) < 21:
        problems.append(f"expected 21 pairs, got {len(pairs)}")
    us_cn = pairs.get("US-CN", {})
    if len(us_cn) < 10 or max(us_cn.values() or [0]) < 1000:
        problems.append("US-CN series implausibly small")
    if prev:
        old = prev.get("pairs", {}).get("US-CN", {}).get("2019")
        new = us_cn.get("2019")
        if old and new and abs(new - old) / old > 0.35:
            problems.append(f"US-CN 2019 count jumped {old}->{new}; API semantics may have changed")
    return problems
