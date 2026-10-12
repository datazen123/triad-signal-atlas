"""Builds the self-contained page from curated data, live data and health.

Output: site/index.html (deployed to GitHub Pages). The same file can be
published anywhere as one HTML file; all data is embedded.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CURATED, DATA, LIVE, ROOT, now_iso, read_json  # noqa: E402

TEMPLATE = ROOT / "template" / "atlas.html"
OUT = ROOT / "site" / "index.html"
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
        "links": {"healed": links.get("healed", {}), "counts": links.get("counts", {})},
    }


def render(data: dict) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if tpl.count(PLACEHOLDER) != 1:
        raise SystemExit("template must contain the data placeholder exactly once")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return tpl.replace(PLACEHOLDER, blob)


def check(html: str, data: dict) -> list[str]:
    problems = []
    if len(html.encode()) > MAX_BYTES:
        problems.append(f"page is {len(html.encode())} bytes, over the limit")
    for key in ("sources", "channels", "projects", "people"):
        if not data[key]:
            problems.append(f"no {key} in curated data")
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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    (OUT.parent / ".nojekyll").write_text("")
    print(f"built {OUT.relative_to(ROOT)} ({len(html.encode()) // 1024} KB, live datasets: {', '.join(data['live']) or 'none yet'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
