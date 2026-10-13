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
from common import CURATED, DATA, LIVE, ROOT, now_iso, read_json  # noqa: E402

TEMPLATE = ROOT / "template" / "atlas.html"
OUT = ROOT / "site" / "index.html"
OUT_ARTIFACT = ROOT / "site" / "artifact.html"
BODY_MARK = '<div class="wrap">'
TITLE = "Triad Signal Atlas"
DESCRIPTION = ("Primary evidence on how the US, China, Russia and the other powers relate: channels, joint projects, "
               "bridge people, live data, and a Peace Lab of playable approaches to building peace.")
PLACEHOLDER = "/*__ATLAS_DATA__*/"
LIVE_KEYS = ["openalex", "nobel", "fedreg", "comtrade", "portwatch", "satcat", "migrants"]
MAX_BYTES = 15 * 1024 * 1024


def repo_urls():
    repo = os.environ.get("GITHUB_REPOSITORY", "datazen123/triad-signal-atlas")
    owner, name = repo.split("/", 1)
    return f"https://{owner}.github.io/{name}/", f"https://github.com/{repo}"


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
        "links": {"healed": links.get("healed", {}), "counts": links.get("counts", {})},
    }


def render(data: dict) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if tpl.count(PLACEHOLDER) != 1:
        raise SystemExit("template must contain the data placeholder exactly once")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return tpl.replace(PLACEHOLDER, blob)


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
        '<meta property="og:site_name" content="Triad Signal Atlas">',
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
