# Common Ground Atlas: context for Claude Code

## What this is
Common Ground Atlas (formerly Triad Signal Atlas) is an evidence board on how the world's leaders and powers relate, plus a Peace Lab. It started with the US–China–Russia triad; the second view adds the EU, India, Japan and the UK. `BACKLOG.md` plans a version for all peoples, not just states.

The display name lives in one place: `ATLAS_NAME` in `pipeline/common.py`. `build.py` replaces every `__ATLAS_NAME__` in the template with it, and `notify.py` uses it in alerts. The repo, the Pages URL, the user agent and the localStorage keys keep their old `triad`/`peacelab` names on purpose, so links and saved journals keep working. Everything is one self-contained HTML page (`site/index.html`) built from `template/atlas.html` plus JSON data. A zero-token pipeline (GitHub Actions + standard-library Python) keeps it updated. The owner is Data (Alex Kim), GitHub `datazen123`.

The page is also published as a claude.ai artifact, which is a static snapshot: https://claude.ai/artifact/3gN2WL2M1QJLGAS7r1Wqr9
The auto-updating version is live at https://datazen123.github.io/triad-signal-atlas/

## Owner's standing preferences
- Use primary, official sources: governments, intergovernmental bodies, universities, academies, peer-reviewed journals, the project's own site. Avoid SEO blogs, AI content farms and "power blogger" sites.
- Use Chinese-language web search queries; report and respond in English.
- Every curated entry needs a source URL (the tests enforce this). Never invent URLs. If a fact can't be confirmed, mark it (`confidence: "medium"`, or empty `links` for channels, which the page shows as "unconfirmed").
- The pipeline must stay zero-token: no AI calls at runtime, standard library only.

## Layout
- `data/curated/`: hand-checked evidence, 116 sources, 76 channels, 55 projects and 80 people.
  - `sources.json`: evidence class A–F, `cov` = countries covered, `topics`.
  - `channels.json`: a dict keyed by id, holding dyad, status, desc, links, asof and note.
  - `projects.json`: start, end, members (US/CN/RU/EU/IN/JP/UK), achieved, url, confidence.
  - `people.json`: from, to, type (resident or envoy), cat, years, did, url, caveat, confidence.
  - `peace.json`: the Peace Lab. Approach nodes (domain, scale, phase, horizon, tags, what/why/mvp/q, play.engine, src, url, conf `ok` or `check`), the 16-card deck, the creation loop, practices by cadence, words for peace and shared problems. Nodes marked `check` show a "check source" flag until verified.
  - `bridges.json` (optional): "Bridges across divides" stories. `build.py` (`load_bridges`) keeps only well-formed stories (id, pair of two, title, what, at least one http(s) source; unknown conf becomes `unconfirmed`), injects an empty set when the file is missing, and the page then hides the view. `ATLAS_BRIDGES=<path>` previews another file, e.g. `pipeline/tests/fixtures/bridges_sample.json` (fictional, tests only).
- Peace Lab v2 on the page:
  - The dome: prompts drift on the inner wall of a sky-sphere around the shape (questions in Contemplate, approach names elsewhere, bridge titles in a ~1-in-7 slot). Tap one to start Contemplate, open the play card, or open the bridge card. Capped at 5/4/3/2 by canvas width.
  - `schedPick` (between `/*SCHED:BEGIN*/` and `/*SCHED:END*/` in the template) is the fairness scheduler: never-shown and never-opened boosts, a 20-minute cool-down, domain balance. Tests run it under node. Per-viewer history: localStorage `peacelab.seen.v1` (`a:`/`q:`/`b:` ids, shown/opened counts).
- `data/live/`: collector outputs (last-known-good). Suspect results go to `quarantine/`.
- `data/health.json`: per-collector status, failure streaks, alerts.
- `pipeline/`:
  - `common.py`: http with backoff, `try_variants`.
  - `doctor.py`: runs due collectors, validation, circuit breaker, alerts.
  - `build.py`: injects data into the template.
  - `notify.py`: GitHub issue labelled `pipeline-health` with an @mention, plus optional SMTP email. Auto-closes on recovery.
  - `collectors/`: openalex, nobel, fedreg, comtrade, portwatch, satcat, migrants, links.
  - `tests/`: offline fixtures plus self-healing tests (`python -m unittest discover -s pipeline/tests -v`).
  - `API_NOTES.md`: what was verified about each upstream API.
- `.github/workflows/update.yml`: daily cron (06:17 UTC). It runs the tests, then doctor, build, commit, Pages deploy and notify.

## Current state (as of 2026-10-14)
- Live on Pages: https://datazen123.github.io/triad-signal-atlas/ (deployed by the workflow; all 8 collectors ok).
- Merged: Peace Lab (#2), bridges (#3), Peace Lab v2 dome + rename (#5), seven-power channels/sources (#6, includes #1 and #4).
- Curated data: 116 sources, 76 channels across all 21 pairs of the seven powers plus Multilateral, 49 bridge stories, 75 Peace Lab nodes (72 ok, 3 check: harmony, hongik, sustained-dialogue).
- The artifact declares `downloads` and `sample` ("Deepen with Claude" appears when the viewer grants it).

## Next steps
1. Verify the last 3 `check` nodes by hand in a normal browser (ctext.org and law.go.kr block automation).
2. Integration with Record Field, Agora, News Engine and Left Behind Ledger: see the owner's launch answers before starting.
3. Optional: SMTP and `CONTACT_EMAIL` secrets; move Actions off Node 20; a light theme.

## Conventions
- After editing the template or data, run `python pipeline/build.py`, then syntax-check the embedded script before committing:

  ```
  sed -n '/<script>/,/<\/script>/p' site/index.html | sed '1d;$d' > /tmp/c.js && node --check /tmp/c.js
  ```

- Commit messages end with the co-author lines used in the git history.
