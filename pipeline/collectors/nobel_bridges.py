"""Nobel laureates born in one power whose prize-winning affiliation was in another.

Source: the Nobel Foundation's own API. A hard, official way to count
'people from A contributing in B'.
"""
from common import get_json, try_variants

NAME = "nobel"
TITLE = "Cross-border Nobel laureates (Nobel Foundation API)"
EVERY_DAYS = 30
SOURCE_URL = "https://www.nobelprize.org/about/developer-zone-2/"

EU_STATES = {
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
    "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "the Netherlands", "Netherlands",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
}
NAME_TO_CODE = {
    "USA": "US", "United States": "US", "United States of America": "US",
    "China": "CN", "People's Republic of China": "CN",
    "Russia": "RU", "Russian Federation": "RU",
    "United Kingdom": "UK", "Scotland": "UK", "England": "UK", "Northern Ireland": "UK", "Wales": "UK",
    "India": "IN", "Japan": "JP",
}


def code_for(name):
    if not name:
        return None
    if name in NAME_TO_CODE:
        return NAME_TO_CODE[name]
    if name in EU_STATES:
        return "EU"
    return None


def _en(obj, *path):
    for p in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(p)
    return obj if isinstance(obj, str) else None


def _page(offset):
    url = f"https://api.nobelprize.org/2.1/laureates?limit=100&offset={offset}"
    _, data = try_variants([
        ("v2.1", lambda: get_json(url)),
        ("v2.0", lambda: get_json(url.replace("/2.1/", "/2/"))),
    ])
    return data


def _profile_link(lau):
    for l in lau.get("links", []) or []:
        href = l.get("href", "") if isinstance(l, dict) else ""
        if "www.nobelprize.org" in href:
            return href
    return None


def collect(prev):
    people, scanned, offset = [], 0, 0
    while offset < 3000:
        data = _page(offset)
        rows = data.get("laureates", [])
        if not rows:
            break
        for lau in rows:
            scanned += 1
            born = code_for(_en(lau, "birth", "place", "countryNow", "en"))
            if not born:
                continue
            for prize in lau.get("nobelPrizes", []) or []:
                tos = sorted({code_for(_en(a, "countryNow", "en")) for a in prize.get("affiliations", []) or []} - {None, born})
                if not tos:
                    continue
                people.append({
                    "name": _en(lau, "fullName", "en") or _en(lau, "knownName", "en"),
                    "from": born, "to": tos,
                    "year": int(prize.get("awardYear", 0) or 0),
                    "category": _en(prize, "category", "en"),
                    "url": _profile_link(lau),
                })
        offset += 100
        if not (data.get("links") or {}).get("next"):
            break
    pairs = {}
    for p in people:
        for t in p["to"]:
            k = f"{p['from']}>{t}"
            pairs[k] = pairs.get(k, 0) + 1
    return {"people": people, "pairs": pairs, "laureates_scanned": scanned}


def validate(payload, prev):
    problems = []
    if payload.get("laureates_scanned", 0) < 900:
        problems.append(f"only {payload.get('laureates_scanned')} laureates scanned")
    if payload.get("pairs", {}).get("EU>US", 0) < 10:
        problems.append("EU>US laureate count implausibly low; field names may have changed")
    return problems
