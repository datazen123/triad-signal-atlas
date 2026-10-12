"""People born in one power living in another (UN DESA International Migrant Stock).

Parses the official origin-by-destination workbook with the standard library
(xlsx is a zip of XML files), so no spreadsheet package is needed.
"""
import io
import re
import zipfile
import xml.etree.ElementTree as ET

from common import http_get, try_variants

NAME = "migrants"
TITLE = "Migrant stock between powers (UN DESA)"
EVERY_DAYS = 30
SOURCE_URL = "https://www.un.org/development/desa/pd/content/international-migrant-stock"

URLS = [
    "https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx",
    "https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx",
]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

POWER_NAMES = {
    "United States of America": "US", "China": "CN", "Russian Federation": "RU",
    "United Kingdom": "UK", "United Kingdom of Great Britain and Northern Ireland": "UK",
    "India": "IN", "Japan": "JP",
}
EU = {"Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia",
      "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia",
      "Lithuania", "Luxembourg", "Malta", "Netherlands", "Netherlands (Kingdom of the)",
      "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"}


def _power(name):
    n = re.sub(r"[*\d]+$", "", (name or "").strip()).strip()
    if n in POWER_NAMES:
        return POWER_NAMES[n]
    return "EU" if n in EU else None


def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def _rows(zf: zipfile.ZipFile):
    shared = []
    if "xl/sharedStrings.xml" in zf.namelist():
        for si in ET.parse(zf.open("xl/sharedStrings.xml")).getroot().findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    wb = ET.parse(zf.open("xl/workbook.xml")).getroot()
    rels = ET.parse(zf.open("xl/_rels/workbook.xml.rels")).getroot()
    target = {r.get("Id"): r.get("Target") for r in rels}
    sheet_path = None
    for s in wb.find("m:sheets", NS):
        if re.search(r"table\s*1\b", s.get("name", ""), re.I):
            sheet_path = "xl/" + target[s.get(REL)].lstrip("/").removeprefix("xl/")
            break
    if not sheet_path:
        raise RuntimeError("sheet 'Table 1' not found; workbook layout changed")
    for _, el in ET.iterparse(zf.open(sheet_path)):
        if el.tag != f"{{{NS['m']}}}row":
            continue
        row = {}
        for c in el.findall("m:c", NS):
            v = c.find("m:v", NS)
            t = c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
            elif v is None:
                continue
            elif t == "s":
                val = shared[int(v.text)]
            else:
                val = v.text
            row[_col_index(c.get("r"))] = val
        el.clear()
        yield row


def _parse(raw: bytes):
    zf = zipfile.ZipFile(io.BytesIO(raw))
    dest_col = orig_col = year_col = None
    year = None
    pairs = {}
    for row in _rows(zf):
        if dest_col is None:
            # The 2024 title cell reads "...: Destination and origin", so a label cell
            # must name one side only, or both columns would lock onto the title.
            texts = {i: str(v).lower() for i, v in row.items()}
            d = [i for i, t in texts.items() if "destination" in t and "origin" not in t and "code" not in t]
            o = [i for i, t in texts.items() if "origin" in t and "destination" not in t and "code" not in t]
            if not (d and o):
                continue
            dest_col, orig_col = d[0], o[0]
        if year_col is None:
            # The year header may sit on the same row as the labels or on the next one.
            yrs = {i: int(float(v)) for i, v in row.items()
                   if i > orig_col and re.fullmatch(r"\d{4}(\.0)?", str(v)) and 1990 <= float(v) <= 2030}
            if yrs:
                year = max(yrs.values())
                year_col = min(i for i, y in yrs.items() if y == year)  # first block = both sexes
            continue
        dp, op = _power(row.get(dest_col)), _power(row.get(orig_col))
        if not dp or not op or dp == op:
            continue
        try:
            val = float(row.get(year_col))
        except (TypeError, ValueError):
            continue
        k = f"{op}>{dp}"
        pairs[k] = pairs.get(k, 0) + val
    if year_col is None:
        raise RuntimeError("could not locate destination/origin/year columns")
    return {"year": year, "pairs": {k: int(v) for k, v in sorted(pairs.items())}}


def collect(prev):
    variants = [(u.rsplit("/", 1)[-1], lambda u=u: _parse(http_get(u, timeout=180))) for u in URLS]
    label, result = try_variants(variants)
    result["file"] = label
    return result


def validate(payload, prev):
    p = payload.get("pairs", {})
    problems = []
    if p.get("CN>US", 0) < 500_000:
        problems.append(f"China-born in US implausibly low ({p.get('CN>US')})")
    if len(p) < 15:
        problems.append(f"only {len(p)} pairs parsed")
    return problems
