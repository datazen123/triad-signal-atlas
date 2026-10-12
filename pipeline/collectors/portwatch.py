"""Daily ship transits through key chokepoints (IMF PortWatch, from satellite AIS)."""
import datetime as dt

from common import get_json, q, today, try_variants

NAME = "portwatch"
TITLE = "Chokepoint ship transits (IMF PortWatch)"
EVERY_DAYS = 7
SOURCE_URL = "https://portwatch.imf.org"

SERVICE = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
           "Daily_Chokepoints_Data/FeatureServer/0/query")
DAYS = 180


def _date(v):
    if isinstance(v, (int, float)):  # ArcGIS sometimes returns epoch milliseconds
        return dt.datetime.fromtimestamp(v / 1000, dt.timezone.utc).date().isoformat()
    return str(v)[:10]


def _fetch(where: str):
    feats, offset = [], 0
    while offset < 20000:
        url = (f"{SERVICE}?where={q(where)}&outFields=date,portname,n_total,n_tanker"
               f"&orderByFields=date%20DESC&resultOffset={offset}&resultRecordCount=2000&f=json")
        data = get_json(url)
        if "error" in data:
            raise RuntimeError(f"ArcGIS error: {data['error']}")
        batch = data.get("features", [])
        feats += batch
        if not data.get("exceededTransferLimit") or not batch:
            break
        offset += len(batch)
    return feats


def collect(prev):
    since = (today() - dt.timedelta(days=DAYS)).isoformat()
    _, feats = try_variants([
        ("date-string", lambda: _fetch(f"date >= '{since}'")),
        ("date-timestamp", lambda: _fetch(f"date >= timestamp '{since} 00:00:00'")),
        ("latest-any", lambda: _fetch("1=1")),
    ])
    weekly = {}
    for f in feats:
        a = f.get("attributes", {})
        name, day = a.get("portname"), _date(a.get("date"))
        if not name or not day:
            continue
        d = dt.date.fromisoformat(day)
        if (today() - d).days > DAYS:
            continue
        wk = (d - dt.timedelta(days=d.weekday())).isoformat()
        cell = weekly.setdefault(name, {}).setdefault(wk, {"total": 0, "tanker": 0})
        cell["total"] += int(a.get("n_total") or 0)
        cell["tanker"] += int(a.get("n_tanker") or 0)
    ranked = sorted(weekly, key=lambda n: -sum(c["total"] for c in weekly[n].values()))[:10]
    latest = max((wk for n in weekly for wk in weekly[n]), default=None)
    return {"chokepoints": {n: dict(sorted(weekly[n].items())) for n in ranked}, "latest_week": latest}


def validate(payload, prev):
    cps = payload.get("chokepoints", {})
    problems = []
    if len(cps) < 5:
        problems.append(f"only {len(cps)} chokepoints returned")
    if not payload.get("latest_week"):
        problems.append("no dated rows")
    return problems
