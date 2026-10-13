"""Builds the self-contained page from curated data, live data and health.

Outputs:
  site/index.html     the full document for GitHub Pages: doctype, charset, viewport,
                      description and Open Graph tags wrapped around the template.
  site/artifact.html  the same page unwrapped, for publishing as a claude.ai artifact
                      (the artifact host adds its own document skeleton).
All data is embedded; neither file makes network calls for data.
"""
from __future__ import annotations

import html as htmllib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ATLAS_NAME, CURATED, DATA, LIVE, ROOT, now_iso, read_json  # noqa: E402

TEMPLATE = ROOT / "template" / "atlas.html"
OUT = ROOT / "site" / "index.html"
OUT_ARTIFACT = ROOT / "site" / "artifact.html"
BODY_MARK = '<div class="wrap">'
TITLE = ATLAS_NAME
NAME_MARK = "__ATLAS_NAME__"  # every occurrence in the template becomes ATLAS_NAME
DESCRIPTION = ("Primary evidence on how the world's leaders and powers relate, starting with the US, China and Russia: "
               "channels, joint projects, bridge people, live data, and a Peace Lab of playable approaches to building peace.")
PLACEHOLDER = "/*__ATLAS_DATA__*/"
LIVE_KEYS = ["openalex", "nobel", "fedreg", "comtrade", "portwatch", "satcat", "migrants"]
MAX_BYTES = 15 * 1024 * 1024

# "Bridges across divides": optional curated stories. If the file is missing, the page gets an empty set
# and hides the feature. ATLAS_BRIDGES overrides the path (for previewing a fixture locally).
BRIDGES = CURATED / "bridges.json"
BRIDGE_KINDS = {"disaster-aid", "rescue", "statement", "cultural", "humanitarian", "economic", "personal", "institutional"}
BRIDGE_CONF = {"ok", "check", "unconfirmed"}


def repo_urls():
    repo = os.environ.get("GITHUB_REPOSITORY", "datazen123/triad-signal-atlas")
    owner, name = repo.split("/", 1)
    return f"https://{owner}.github.io/{name}/", f"https://github.com/{repo}"


def _text(v) -> str:
    return v.strip() if isinstance(v, str) else ""


def load_bridges(path=None, warn=print) -> dict:
    """Reads bridges.json and keeps only well-formed stories, so one bad entry can't break the page.

    A story needs an id, a pair of two codes, a title, a "what", and at least one http(s) source.
    An unknown kind becomes "personal"; an unknown or missing confidence becomes "unconfirmed", which
    the page flags. Anything dropped is reported on stdout, never silently patched into a claim."""
    path = Path(path or os.environ.get("ATLAS_BRIDGES") or BRIDGES)
    empty = {"about": "", "verified": "", "stories": []}
    if not path.exists():
        return empty
    doc = read_json(path)
    if not isinstance(doc, dict):
        warn(f"bridges: {path.name} is not a readable JSON object; feature hidden")
        return empty
    stories, seen = [], set()
    for i, st in enumerate(doc.get("stories") or []):
        if not isinstance(st, dict):
            warn(f"bridges: story #{i} is not an object; skipped")
            continue
        sid, pair = _text(st.get("id")), st.get("pair")
        src = [{"label": _text(x.get("label")) or _text(x.get("url")), "url": _text(x.get("url")), "lang": _text(x.get("lang"))}
               for x in (st.get("src") or []) if isinstance(x, dict) and _text(x.get("url")).startswith(("http://", "https://"))]
        why = []
        if not sid or sid in seen:
            why.append("missing or duplicate id")
        if not (isinstance(pair, list) and len(pair) == 2 and all(_text(p) for p in pair)):
            why.append("pair must be two codes")
        if not _text(st.get("title")) or not _text(st.get("what")):
            why.append("needs title and what")
        if not src:
            why.append("needs at least one http(s) source")
        if why:
            warn(f"bridges: story {sid or '#' + str(i)} skipped ({'; '.join(why)})")
            continue
        seen.add(sid)
        sides = st.get("sides")
        if not (isinstance(sides, list) and len(sides) == 2):
            sides = pair
        stories.append({
            "id": sid,
            "pair": [_text(p) for p in pair],
            "sides": [_text(x) or _text(p) for x, p in zip(sides, pair)],
            "year": _text(str(st.get("year") or "")),
            "kind": st.get("kind") if st.get("kind") in BRIDGE_KINDS else "personal",
            "who": _text(st.get("who")),
            "title": _text(st.get("title")),
            "what": _text(st.get("what")),
            "why_it_matters": _text(st.get("why_it_matters")),
            "src": src,
            "conf": st.get("conf") if st.get("conf") in BRIDGE_CONF else "unconfirmed",
            "note": _text(st.get("note")),
        })
    return {"about": _text(doc.get("about")), "verified": _text(doc.get("verified")), "stories": stories}


def compose() -> dict:
    channels = read_json(CURATED / "channels.json", {}) or {}
    live = {}
    for key in LIVE_KEYS:
        doc = read_json(LIVE / f"{key}.json")
        if doc and doc.get("payload"):
            live[key] = {k: doc.get(k) for k in ("title", "source_url", "collected_at", "payload")}
    links = (read_json(LIVE / "links.json") or {}).get("payload") or {}
    health = read_json(DATA / "health.json", {}) or {}
    for e in health.get("collectors", {}).values():
        e.pop("trace", None)  # stack traces belong in the issue, not on the public page
    live_url, repo_url = repo_urls()
    return {
        "name": TITLE,
        "built_at": now_iso(),
        "live_url": live_url,
        "repo_url": repo_url,
        "sources": read_json(CURATED / "sources.json", []),
        "channels": [{"id": k, **v} for k, v in channels.items()],
        "projects": read_json(CURATED / "projects.json", []),
        "people": read_json(CURATED / "people.json", []),
        "live": live,
        "health": health,
        "peace": read_json(CURATED / "peace.json", {}) or {},
        "bridges": load_bridges(),
        "links": {"healed": links.get("healed", {}), "counts": links.get("counts", {})},
    }


def render(data: dict) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if tpl.count(PLACEHOLDER) != 1:
        raise SystemExit("template must contain the data placeholder exactly once")
    if NAME_MARK not in tpl:
        raise SystemExit(f"template must use the {NAME_MARK} placeholder for the display name")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # The name goes in before the data, so a data string that happens to contain the mark stays untouched.
    return tpl.replace(NAME_MARK, htmllib.escape(TITLE)).replace(PLACEHOLDER, blob)


def wrap(page: str, live_url: str) -> str:
    """Wraps the template output in a standards-mode document for GitHub Pages."""
    if page.count(BODY_MARK) != 1:
        raise SystemExit(f"template must contain {BODY_MARK!r} exactly once")
    head, body = page.split(BODY_MARK, 1)
    e = htmllib.escape
    meta = "\n".join([
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        '<meta name="color-scheme" content="dark">',
        '<meta name="theme-color" content="#0a0f1e">',
        f'<meta name="description" content="{e(DESCRIPTION)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{e(TITLE)}">',
        f'<meta property="og:description" content="{e(DESCRIPTION)}">',
        f'<meta property="og:url" content="{e(live_url)}">',
        f'<meta property="og:site_name" content="{e(TITLE)}">',
        '<meta name="twitter:card" content="summary">',
        f'<meta name="twitter:title" content="{e(TITLE)}">',
        f'<meta name="twitter:description" content="{e(DESCRIPTION)}">',
        f'<link rel="canonical" href="{e(live_url)}">',
        "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Ccircle cx='16' cy='16' r='14' fill='%230a0f1e'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%239fe6d6'/%3E%3C/svg%3E\">",
    ])
    return f"{meta}\n{head.strip()}\n</head>\n<body>\n{BODY_MARK}{body.rstrip()}\n</body>\n</html>\n"


def check(html: str, data: dict) -> list[str]:
    problems = []
    if len(html.encode()) > MAX_BYTES:
        problems.append(f"page is {len(html.encode())} bytes, over the limit")
    for key in ("sources", "channels", "projects", "people"):
        if not data[key]:
            problems.append(f"no {key} in curated data")
    if not (data.get("peace") or {}).get("nodes"):
        problems.append("no Peace Lab nodes in curated data (data/curated/peace.json)")
    start = html.index('type="application/json">') + len('type="application/json">')
    end = html.index("</script>", start)
    json.loads(html[start:end])  # raises if the embedded data is not valid JSON
    return problems


def main() -> int:
    data = compose()
    html = render(data)
    problems = check(html, data)
    if problems:
        print("BUILD FAILED:", *problems, sep="\n  ")
        return 1
    page = wrap(html, data["live_url"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    OUT_ARTIFACT.write_text(html, encoding="utf-8")
    (OUT.parent / ".nojekyll").write_text("")
    print(f"built {OUT.relative_to(ROOT)} ({len(page.encode()) // 1024} KB) and {OUT_ARTIFACT.relative_to(ROOT)} (unwrapped), "
          f"live datasets: {', '.join(data['live']) or 'none yet'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
