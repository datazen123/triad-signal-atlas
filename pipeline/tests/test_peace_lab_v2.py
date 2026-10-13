"""Peace Lab v2: display-name constant, the optional bridges.json hook, and the dome's fairness scheduler.

The scheduler is JavaScript inside the template. Its pure core sits between /*SCHED:BEGIN*/ and
/*SCHED:END*/, and these tests run it under node when node is installed (it is on GitHub's runners).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPE))

import build  # noqa: E402
import common  # noqa: E402
import notify  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bridges_sample.json"
NODE = shutil.which("node")


def embedded_data(html):
    start = html.index('type="application/json">') + len('type="application/json">')
    return json.loads(html[start:html.index("</script>", start)])


def inline_scripts(html):
    return re.findall(r"<script>(.*?)</script>", html, flags=re.S)


class DisplayNameTests(unittest.TestCase):
    def test_one_constant_feeds_build_and_alerts(self):
        self.assertEqual(common.ATLAS_NAME, "Common Ground Atlas")
        self.assertEqual(build.TITLE, common.ATLAS_NAME)
        self.assertIn(common.ATLAS_NAME, notify.render([], "failure", "https://example.org/run", "someone"))

    def test_name_is_applied_everywhere_in_the_page(self):
        data = build.compose()
        html = build.render(data)
        page = build.wrap(html, data["live_url"])
        self.assertNotIn(build.NAME_MARK, html)
        self.assertNotIn("Triad Signal Atlas", page)
        self.assertIn(f"<title>{common.ATLAS_NAME}</title>", html)
        self.assertIn(f'<h1 class="name">{common.ATLAS_NAME}</h1>', html)
        self.assertIn(f'property="og:site_name" content="{common.ATLAS_NAME}"', page)
        self.assertEqual(data["name"], common.ATLAS_NAME)

    def test_renaming_is_a_one_line_change(self):
        with mock.patch.object(build, "TITLE", "Another Name"):
            html = build.render(build.compose())
        self.assertIn("<title>Another Name</title>", html)
        self.assertNotIn(common.ATLAS_NAME, html.split('type="application/json">')[0])

    def test_pages_url_and_repo_are_unchanged(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GITHUB_REPOSITORY", None)
            live, repo = build.repo_urls()
        self.assertEqual(live, "https://datazen123.github.io/triad-signal-atlas/")
        self.assertEqual(repo, "https://github.com/datazen123/triad-signal-atlas")


class BridgesHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        os.environ.pop("ATLAS_BRIDGES", None)

    def tearDown(self):
        self.env.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build_with(self, path):
        with mock.patch.object(build, "BRIDGES", path):
            data = build.compose()
            html = build.render(data)
        self.assertEqual(build.check(html, data), [])
        return data, html

    def test_absent_file_injects_an_empty_set(self):
        data, html = self.build_with(self.tmp / "missing.json")
        self.assertEqual(data["bridges"], {"about": "", "verified": "", "stories": []})
        self.assertEqual(embedded_data(html)["bridges"]["stories"], [])
        # the section ships hidden; the script only reveals it when there are stories
        self.assertIn('<section id="sec-divides" aria-labelledby="h-div" hidden>', html)
        self.assertIn('id="navDiv" hidden', html)

    def test_fixture_is_injected_and_sanitised(self):
        notes = []
        doc = build.load_bridges(FIXTURE, warn=notes.append)
        ids = [s["id"] for s in doc["stories"]]
        self.assertEqual(ids, ["fx-ok", "fx-check", "fx-unconfirmed"])
        self.assertTrue(any("fx-no-source" in n for n in notes), notes)
        by = {s["id"]: s for s in doc["stories"]}
        self.assertEqual(by["fx-unconfirmed"]["conf"], "unconfirmed")  # "maybe" is not a confidence level
        self.assertEqual(by["fx-unconfirmed"]["kind"], "personal")  # unknown kind falls back
        self.assertEqual(by["fx-check"]["conf"], "check")
        self.assertEqual(by["fx-ok"]["sides"], ["Fixture side A", "Fixture side B"])
        self.assertEqual(doc["verified"], "2026-10-13")

        shutil.copy(FIXTURE, self.tmp / "bridges.json")
        data, html = self.build_with(self.tmp / "bridges.json")
        self.assertEqual([s["id"] for s in embedded_data(html)["bridges"]["stories"]], ids)

    def test_env_override_for_local_preview(self):
        os.environ["ATLAS_BRIDGES"] = str(FIXTURE)
        self.assertEqual(len(build.load_bridges()["stories"]), 3)

    def test_broken_file_hides_the_feature_instead_of_failing(self):
        bad = self.tmp / "bridges.json"
        bad.write_text("{not json", encoding="utf-8")
        notes = []
        self.assertEqual(build.load_bridges(bad, warn=notes.append)["stories"], [])
        self.assertTrue(notes)
        self.build_with(bad)

    def test_html_in_stories_cannot_break_out_of_the_data_block(self):
        doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
        doc["stories"][0]["title"] = "</script><script>alert(1)</script>"
        p = self.tmp / "bridges.json"
        p.write_text(json.dumps(doc), encoding="utf-8")
        data, html = self.build_with(p)
        self.assertEqual(embedded_data(html)["bridges"]["stories"][0]["title"], doc["stories"][0]["title"])


@unittest.skipUnless(NODE, "node is not installed")
class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        data = build.compose()
        cls.html = build.render(data)
        cls.page = build.wrap(cls.html, data["live_url"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def node(self, code):
        f = self.tmp / "t.js"
        f.write_text(code, encoding="utf-8")
        return subprocess.run([NODE, str(f)], capture_output=True, text=True, timeout=60)

    def test_inline_scripts_parse(self):
        for name, html in (("index", self.page), ("artifact", self.html)):
            scripts = inline_scripts(html)
            self.assertTrue(scripts, name)
            for i, code in enumerate(scripts):
                f = self.tmp / f"{name}{i}.js"
                f.write_text(code, encoding="utf-8")
                r = subprocess.run([NODE, "--check", str(f)], capture_output=True, text=True, timeout=60)
                self.assertEqual(r.returncode, 0, f"{name} script {i}: {r.stderr}")

    def sched(self):
        tpl = (PIPE.parent / "template" / "atlas.html").read_text(encoding="utf-8")
        m = re.search(r"/\*SCHED:BEGIN\*/(.*?)/\*SCHED:END\*/", tpl, flags=re.S)
        self.assertIsNotNone(m, "scheduler markers missing from template")
        return m.group(1)

    def simulate(self, body):
        prelude = """
let seed = 42; const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
const peace = JSON.parse(require('fs').readFileSync(process.argv[2] || 0, 'utf8'));
"""
        f = self.tmp / "peace.json"
        f.write_text((common.CURATED / "peace.json").read_text(encoding="utf-8"), encoding="utf-8")
        code = self.sched() + prelude.replace("process.argv[2] || 0", json.dumps(str(f))) + body
        r = self.node(code)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    LOOP = """
const items = peace.nodes.map(n => ({id: 'a:' + n.id, group: n.domain, w: 1}));
const seen = {}; let active = [], now = 1e12; const order = [];
function step() {
  const it = schedPick(items, seen, active, now, rnd); order.push(it.id);
  const s = seen[it.id] || (seen[it.id] = {s: 0, o: 0, l: 0}); s.s++; s.l = now;
  active.push(it.id); if (active.length > 5) active.shift(); now += 3000;
}
"""

    def test_every_approach_surfaces_within_one_pass(self):
        out = self.simulate(self.LOOP + """
for (let i = 0; i < items.length; i++) step();
const firstPass = new Set(order).size;
for (let i = 0; i < items.length; i++) step();
const counts = {}; order.forEach(id => counts[id] = (counts[id] || 0) + 1);
console.log(JSON.stringify({n: items.length, firstPass, total: new Set(order).size,
  maxShown: Math.max(...Object.values(counts))}));
""")
        self.assertEqual(out["total"], out["n"], "an approach never surfaced in two passes")
        self.assertGreaterEqual(out["firstPass"], int(out["n"] * 0.9), out)
        self.assertLessEqual(out["maxShown"], 4, out)

    def test_domains_are_balanced(self):
        out = self.simulate(self.LOOP + """
const dom = Object.fromEntries(items.map(i => [i.id, i.group])), size = {};
items.forEach(i => size[i.group] = (size[i.group] || 0) + 1);
let crowd = 0;
for (let i = 0; i < 45; i++) {
  step();
  const c = {}; active.forEach(id => c[dom[id]] = (c[dom[id]] || 0) + 1);
  crowd = Math.max(crowd, ...Object.values(c));
}
const byDomain = {}; order.forEach(id => byDomain[dom[id]] = (byDomain[dom[id]] || 0) + 1);
console.log(JSON.stringify({byDomain, size, crowd}));
""")
        by, size = out["byDomain"], out["size"]
        self.assertEqual(set(by), set(size), "a domain never surfaced in 45 picks")
        for d, n in by.items():
            fair = 45 * size[d] / 75
            self.assertLessEqual(n, 1.6 * fair + 1, (d, out))
            self.assertGreaterEqual(n, 0.5 * fair, (d, out))
        self.assertLessEqual(out["crowd"], 2, "more than two of one domain on the dome at once")

    def test_never_seen_and_never_opened_come_first(self):
        out = self.simulate(self.LOOP + """
// a returning viewer who has seen and opened everything except five approaches
const fresh = new Set(items.slice(0, 5).map(i => i.id));
items.forEach(i => { if (!fresh.has(i.id)) seen[i.id] = {s: 4, o: 2, l: now - 3600e3}; });
for (let i = 0; i < 5; i++) step();
console.log(JSON.stringify({hits: order.filter(id => fresh.has(id)).length}));
""")
        self.assertGreaterEqual(out["hits"], 4, out)

    def test_just_shown_items_cool_down(self):
        out = self.simulate(self.LOOP + """
const a = items.slice(0, 2);
seen[a[0].id] = {s: 1, o: 0, l: now - 1000}; seen[a[1].id] = {s: 1, o: 0, l: now - 3600e3};
let x = 0, y = 0;
for (let i = 0; i < 4000; i++) { const it = schedPick(a, seen, [], now, rnd); it.id === a[0].id ? x++ : y++; }
console.log(JSON.stringify({recent: x, old: y}));
""")
        self.assertLess(out["recent"] * 10, out["old"], out)

    def test_low_weight_items_still_appear(self):
        out = self.simulate("""
const items = peace.nodes.map(n => ({id: 'a:' + n.id, group: n.domain, w: 1}))
  .concat([0, 1, 2, 3].map(i => ({id: 'b:' + i, group: 'bridge', w: .35})));
const seen = {}; let active = [], now = 1e12, bridges = 0;
for (let i = 0; i < 300; i++) {
  const it = schedPick(items, seen, active, now, rnd); if (it.id.startsWith('b:')) bridges++;
  const s = seen[it.id] || (seen[it.id] = {s: 0, o: 0, l: 0}); s.s++; s.l = now;
  active.push(it.id); if (active.length > 5) active.shift(); now += 3000;
}
console.log(JSON.stringify({bridges}));
""")
        self.assertGreater(out["bridges"], 0, out)
        self.assertLess(out["bridges"], 60, out)


if __name__ == "__main__":
    unittest.main()
