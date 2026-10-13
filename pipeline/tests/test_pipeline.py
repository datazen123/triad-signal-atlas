"""Offline tests: every collector against canned responses, plus the self-healing paths.

Run: python -m unittest discover -s pipeline/tests -v
These run first in CI. If they fail, our code is broken (not an upstream API).
"""
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

PIPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPE))

import common  # noqa: E402
import collectors  # noqa: E402
from collectors import (celestrak_satcat, comtrade_mirror, federal_register, link_health,  # noqa: E402
                        nobel_bridges, openalex_coauthor, portwatch, undesa_migrants)


def J(obj):
    return json.dumps(obj).encode()


def oa_response(url, **_):
    base = 4000 if "CN" in url and "US" in url else 900
    return J({"meta": {"count": 1, "page": 1, "per_page": 200, "groups_count": 26}, "group_by": [{"key": str(y), "key_display_name": str(y), "count": base + (y - 2000) * 50}
                                                   for y in range(2000, 2026)]})


def nobel_response(url, **_):
    off = int(url.split("offset=")[1].split("&")[0])
    if off >= 1000:
        return J({"laureates": [], "meta": {"offset": off, "limit": 100, "count": 1000}, "links": {"first": "x", "self": "x"}})
    people = []
    for i in range(100):
        n = off + i
        born = ["Germany", "China", "Russia", "India", "Japan", "USA"][n % 6]
        aff = "USA" if n % 4 else "United Kingdom"
        people.append({"id": str(n), "fullName": {"en": f"Person {n}"},
                       "birth": {"place": {"countryNow": {"en": born, "sameAs": ["https://www.wikidata.org/wiki/Q1"]}}},
                       "links": [{"rel": "laureate", "href": f"https://api.nobelprize.org/2/laureate/{n}", "types": "application/json"},
                                 {"rel": "external", "href": f"https://www.nobelprize.org/laureate/{n}", "types": "text/html"}],
                       "nobelPrizes": [{"awardYear": str(1950 + n % 70), "category": {"en": "Physics"},
                                        "affiliations": [{"name": {"en": "Univ"}, "country": {"en": aff},
                                                          "countryNow": {"en": aff, "sameAs": ["https://www.wikidata.org/wiki/Q2"]}}]}]})
    return J({"laureates": people, "meta": {"offset": off, "limit": 100, "count": 1000},
              "links": {"first": "x", "self": "x", "next": f"https://api.nobelprize.org/2.1/laureates?offset={off + 100}&limit=100"}})


def fedreg_response(url, **_):
    return J({f"{y}-01-01": {"count": 10 + y % 7, "name": str(y)} for y in range(2012, 2026)})


def comtrade_response(url, **_):
    return J({"elapsedTime": "0.03 secs", "count": 1, "error": "",
              "data": [{"reporterCode": 156, "partnerCode": 643, "flowCode": "X", "period": "2024", "cmdCode": "TOTAL",
                        "customsCode": "C00", "motCode": 0, "partner2Code": 0, "primaryValue": 110935409106.0}]})


def portwatch_response(url, **_):
    feats = []
    for d in range(60):
        day = (common.today() - __import__("datetime").timedelta(days=d)).isoformat()
        for name in ["Suez Canal", "Strait of Hormuz", "Malacca Strait", "Bab el-Mandeb Strait", "Panama Canal", "Bosporus Strait"]:
            feats.append({"attributes": {"date": day, "portname": name, "n_total": 60, "n_tanker": 20}})
    return J({"features": feats, "exceededTransferLimit": False})


def satcat_response(url, **_):
    rows = ["OBJECT_NAME,OBJECT_ID,NORAD_CAT_ID,OBJECT_TYPE,OPS_STATUS_CODE,OWNER,LAUNCH_DATE,LAUNCH_SITE,DECAY_DATE,"
            "PERIOD,INCLINATION,APOGEE,PERIGEE,RCS,DATA_STATUS_CODE,ORBIT_CENTER,ORBIT_TYPE",
            "SPUTNIK 1,1957-001B,2,PAY,D,CIS,1957-10-04,TYMSC,1958-01-03,96.10,65.00,1080,64,,,EA,IMP"]
    for i in range(1500):
        rows.append(f"SAT {i},X,{i},PAY,+,US,2022-01-01,AFETR,,95.1,53.0,550,540,,,EA,ORB")
    for i in range(300):
        rows.append(f"CN {i},X,{i},PAY,+,PRC,2023-05-01,JSC,,95.1,53.0,550,540,,,EA,ORB")
    rows.append("CN DEB,X,9,DEB,D,PRC,2023-05-01,JSC,,95.1,53.0,550,540,,,EA,ORB")
    for code in ("GREC", "POR", "ESA"):
        rows.append(f"{code} SAT,X,1,PAY,+,{code},2021-01-01,FRGUI,,95.1,53.0,550,540,,,EA,ORB")
    rows.append("ISS (ZARYA),1998-067A,25544,PAY,+,ISS,1998-11-20,TYMSC,,92.97,51.63,425,416,399.0524,,EA,ORB")
    return "\n".join(rows).encode()


def make_xlsx():
    """A tiny workbook in the UN DESA layout."""
    shared = ["Region, development group, country or area of destination", "Region, development group, country or area of origin",
              "United States of America*", "China", "Russian Federation", "Germany", "India", "Japan",
              "International Migrant Stock 2024: Destination and origin", "Location code of destination", "Location code of origin",
              "Data type", "Coverage"]

    def t(ref, text):
        return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'
    years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024]
    cols = "HIJKLMNO"  # both sexes; the male block follows in P..W
    head = (t("A11", "Index") + '<c r="B11" t="s"><v>0</v></c>' + '<c r="C11" t="s"><v>12</v></c><c r="D11" t="s"><v>11</v></c>'
            '<c r="E11" t="s"><v>9</v></c><c r="F11" t="s"><v>1</v></c><c r="G11" t="s"><v>10</v></c>'
            + "".join(f'<c r="{c}11"><v>{y}</v></c>' for c, y in zip(cols, years))
            + "".join(f'<c r="{c}11"><v>{y}</v></c>' for c, y in zip("PQRSTUVW", years)))
    rows = ['<row r="2"><c r="D2" t="s"><v>8</v></c></row>',
            '<row r="3">' + t("D3", "Table 1: International migrant stock at mid-year by sex and by region, country or area of destination and origin") + '</row>',
            '<row r="10">' + t("C10", "Migrant notes") + t("Q10", "International migrant stock at mid-year, males") + '</row>',
            f'<row r="11">{head}</row>']
    data = [(2, 3, 2_500_000), (2, 4, 400_000), (2, 6, 2_900_000), (4, 3, 60_000), (3, 4, 35_000), (5, 4, 900_000), (2, 7, 300_000),
            (3, 2, 70_000), (7, 3, 700_000), (4, 2, 30_000), (5, 3, 150_000), (2, 5, 1_200_000), (5, 2, 120_000), (6, 2, 40_000),
            (7, 2, 60_000), (4, 6, 10_000)]
    for r, (d, o, v) in enumerate(data, start=12):
        rows.append(f'<row r="{r}"><c r="A{r}"><v>{r}</v></c><c r="B{r}" t="s"><v>{d}</v></c><c r="D{r}"><v>5</v></c>'
                    f'<c r="E{r}"><v>840</v></c><c r="F{r}" t="s"><v>{o}</v></c><c r="G{r}"><v>156</v></c>'
                    f'<c r="H{r}"><v>1</v></c><c r="O{r}"><v>{v}</v></c><c r="W{r}"><v>{v // 2}</v></c></row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    rns = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook {ns} {rns}><sheets><sheet name="Contents" sheetId="1" r:id="rId1"/><sheet name="Table 1" sheetId="2" r:id="rId2"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet2.xml"/></Relationships>')
        z.writestr("xl/sharedStrings.xml", f'<sst {ns}>' + "".join(f"<si><t>{x}</t></si>" for x in shared) + "</sst>")
        z.writestr("xl/worksheets/sheet1.xml", f"<worksheet {ns}><sheetData/></worksheet>")
        z.writestr("xl/worksheets/sheet2.xml", f"<worksheet {ns}><sheetData>{''.join(rows)}</sheetData></worksheet>")
    return buf.getvalue()


XLSX = make_xlsx()


def router(url, method="GET"):
    if "openalex" in url:
        return oa_response(url)
    if "nobelprize" in url:
        return nobel_response(url)
    if "federalregister" in url:
        return fedreg_response(url)
    if "comtradeapi" in url:
        return comtrade_response(url)
    if "arcgis" in url:
        return portwatch_response(url)
    if "celestrak" in url:
        return satcat_response(url)
    if "undesa" in url:
        return XLSX
    if "archive.org/wayback" in url:
        return J({"archived_snapshots": {"closest": {"available": True, "status": "200", "url": "http://web.archive.org/web/2024/" + url}}})
    if "dead.example" in url:
        raise common.FetchError(url, "HTTP 404", 404)
    if "blocked.example" in url:
        raise common.FetchError(url, "HTTP 403", 403)
    if "timeout.example" in url:
        raise common.FetchError(url, "network: timed out")
    return b"ok"


class Base(unittest.TestCase):
    def setUp(self):
        common.set_transport(router)
        self.tmp = Path(tempfile.mkdtemp())
        for mod in (common,):
            pass
        self.patches = [mock.patch.object(common, "DATA", self.tmp), mock.patch.object(common, "LIVE", self.tmp / "live")]
        for p in self.patches:
            p.start()
        mock.patch("time.sleep", lambda *_: None).start()

    def tearDown(self):
        mock.patch.stopall()
        common.set_transport(None)
        shutil.rmtree(self.tmp, ignore_errors=True)


class CollectorTests(Base):
    def check(self, mod):
        payload = mod.collect(None)
        self.assertEqual(mod.validate(payload, None), [], f"{mod.NAME} failed its own validation")
        return payload

    def test_openalex(self):
        p = self.check(openalex_coauthor)
        self.assertEqual(len(p["pairs"]), 21)
        self.assertEqual(p["pairs"]["US-CN"]["2000"], 4000)

    def test_nobel(self):
        p = self.check(nobel_bridges)
        self.assertGreater(p["pairs"]["EU>US"], 10)
        self.assertNotIn("US>US", p["pairs"])

    def test_fedreg(self):
        p = self.check(federal_register)
        self.assertIn("2020", p["series"]["CN"])

    def test_comtrade(self):
        p = self.check(comtrade_mirror)
        self.assertEqual(len(p["rows"]), 32)

    def test_portwatch(self):
        p = self.check(portwatch)
        self.assertIn("Suez Canal", p["chokepoints"])

    def test_satcat(self):
        p = self.check(celestrak_satcat)
        self.assertEqual(p["active_payloads"]["US"], 1500)
        self.assertEqual(p["active_payloads"]["JOINT"], 1)
        self.assertEqual(p["active_payloads"]["EU"], 3)  # Greece, Portugal and ESA all count as EU
        self.assertNotIn("RU", p["active_payloads"])  # decayed Sputnik is not active

    def test_migrants(self):
        p = self.check(undesa_migrants)
        self.assertEqual(p["year"], 2024)
        self.assertEqual(p["pairs"]["CN>US"], 2_500_000)
        self.assertEqual(p["pairs"]["RU>EU"], 900_000)  # Germany is summed into EU


class SelfHealingTests(Base):
    def test_variant_fallback(self):
        calls = []

        def flaky(url, method="GET"):
            calls.append(url)
            if "authorships.institutions" in url:
                raise common.FetchError(url, "HTTP 400", 400)
            return oa_response(url)
        common.set_transport(flaky)
        p = openalex_coauthor.collect(None)
        self.assertEqual(len(p["pairs"]), 21)
        self.assertTrue(any("filter=institutions.country_code" in u for u in calls))

    def test_doctor_keeps_last_good_and_alerts(self):
        import doctor
        with mock.patch.object(doctor, "LIVE", self.tmp / "live"), mock.patch.object(doctor, "HEALTH", self.tmp / "health.json"):
            doctor.main(["--only", "fedreg"])
            good = json.loads((self.tmp / "live" / "fedreg.json").read_text())
            common.set_transport(lambda url, method="GET": (_ for _ in ()).throw(common.FetchError(url, "HTTP 500", 500)))
            doctor.main(["--only", "fedreg"])
            doctor.main(["--only", "fedreg"])
            health = json.loads((self.tmp / "health.json").read_text())
            entry = health["collectors"]["fedreg"]
            self.assertEqual(entry["status"], "fail")
            self.assertEqual(entry["consecutive_failures"], 2)
            self.assertEqual([a["collector"] for a in health["alerts"]], ["fedreg"])
            still = json.loads((self.tmp / "live" / "fedreg.json").read_text())
            self.assertEqual(still["collected_at"], good["collected_at"], "last good data must survive failures")
            # recovery clears the alert
            common.set_transport(router)
            doctor.main(["--only", "fedreg"])
            health = json.loads((self.tmp / "health.json").read_text())
            self.assertEqual(health["alerts"], [])

    def test_suspect_result_is_quarantined(self):
        import doctor
        with mock.patch.object(doctor, "LIVE", self.tmp / "live"), mock.patch.object(doctor, "HEALTH", self.tmp / "health.json"):
            common.set_transport(lambda url, method="GET": J({"2024-01-01": {"count": 1}}))
            doctor.main(["--only", "fedreg"])
            self.assertFalse((self.tmp / "live" / "fedreg.json").exists())
            self.assertTrue((self.tmp / "live" / "quarantine" / "fedreg.json").exists())
            entry = json.loads((self.tmp / "health.json").read_text())["collectors"]["fedreg"]
            self.assertEqual(entry["status"], "suspect")

    def test_circuit_breaker_backs_off(self):
        import datetime as dt
        import doctor
        now = dt.datetime.now(dt.timezone.utc)
        yesterday = (now - dt.timedelta(days=1, hours=1)).isoformat()
        self.assertTrue(doctor.due({"last_attempt": yesterday, "status": "fail", "consecutive_failures": 1}, 30, now))
        self.assertFalse(doctor.due({"last_attempt": yesterday, "status": "fail", "consecutive_failures": 3}, 3, now))

    def test_dead_link_healed_after_two_runs(self):
        with mock.patch.object(link_health, "all_urls", lambda: ["https://dead.example/x", "https://blocked.example/y", "https://ok.example/z"]):
            first = link_health.collect(None)
            self.assertEqual(first["healed"], {})
            second = link_health.collect(first)
            self.assertIn("https://dead.example/x", second["healed"])
            self.assertTrue(second["healed"]["https://dead.example/x"].startswith("https://web.archive.org/"))
            self.assertEqual(second["status"]["https://blocked.example/y"]["state"], "unverifiable")
            self.assertEqual(link_health.validate(second, first), [])

    def test_timeout_is_unreachable_not_healed(self):
        with mock.patch.object(link_health, "all_urls", lambda: ["https://timeout.example/x", "https://ok.example/z"]):
            first = link_health.collect(None)
            second = link_health.collect(first)
            self.assertEqual(second["status"]["https://timeout.example/x"]["state"], "unreachable")
            self.assertEqual(second["healed"], {}, "a site that only times out must not be swapped for an archive copy")


class RegistryAndBuildTests(unittest.TestCase):
    def test_registry_contract(self):
        names = set()
        for mod in collectors.ALL:
            for attr in ("NAME", "TITLE", "EVERY_DAYS", "SOURCE_URL", "collect", "validate"):
                self.assertTrue(hasattr(mod, attr), f"{mod.__name__} lacks {attr}")
            self.assertNotIn(mod.NAME, names)
            names.add(mod.NAME)

    def test_build_renders(self):
        import build
        data = build.compose()
        html = build.render(data)
        self.assertNotIn(build.PLACEHOLDER, html)
        self.assertEqual(build.check(html, data), [])

    def test_pages_output_is_a_full_document(self):
        import build
        data = build.compose()
        page = build.wrap(build.render(data), data["live_url"])
        self.assertTrue(page.startswith("<!doctype html>"), "Pages output must be standards mode")
        for needle in ('<meta charset="utf-8">', 'name="viewport"', "viewport-fit=cover", 'name="description"',
                       'property="og:title"', 'property="og:url"', "<body>", "</html>"):
            self.assertIn(needle, page)
        self.assertLess(page.index("</head>"), page.index('<div class="wrap">'))
        self.assertEqual(page.count("<title>"), 1)

    def test_artifact_output_stays_unwrapped(self):
        import build
        html = build.render(build.compose())
        self.assertNotIn("<!doctype", html.lower())
        self.assertNotIn("<html", html.lower())

    def test_curated_people_and_projects_are_sourced(self):
        for name in ("people", "projects"):
            for item in common.read_json(common.CURATED / f"{name}.json"):
                self.assertTrue(item.get("url", "").startswith("http"), f"{name}: {item.get('id')} has no source URL")


if __name__ == "__main__":
    unittest.main()
