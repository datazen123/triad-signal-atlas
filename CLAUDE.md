# Common Ground Atlas: context for Claude Code

## What this is
Common Ground Atlas (formerly Triad Signal Atlas) is an evidence board on how the world's leaders and powers relate, plus a Peace Lab. It started with the US–China–Russia triad; the second view adds the EU, India, Japan and the UK. `BACKLOG.md` plans a version for all peoples, not just states.

The display name lives in one place: `ATLAS_NAME` in `pipeline/common.py`. `build.py` replaces every `__ATLAS_NAME__` in the template with it, and `notify.py` uses it in alerts. The repo, the Pages URL, the user agent and the localStorage keys keep their old `triad`/`peacelab` names on purpose, so links and saved journals keep working. Everything is one self-contained HTML page (`site/index.html`) built from `template/atlas.html` plus JSON data. A zero-token pipeline (GitHub Actions + standard-library Python) keeps it updated. The owner is Data (Alex Kim), GitHub `datazen123`.

The page is also published as a claude.ai artifact, which is a static snapshot: https://claude.ai/artifact/3gN2WL2M1QJLGAS7r1Wqr9
The auto-updating version will live at https://datazen123.github.io/triad-signal-atlas/ once the repo is pushed and Pages is on.

## Owner's standing preferences
- Use primary, official sources: governments, intergovernmental bodies, universities, academies, peer-reviewed journals, the project's own site. Avoid SEO blogs, AI content farms and "power blogger" sites.
- Use Chinese-language web search queries; report and respond in English.
- Every curated entry needs a source URL (the tests enforce this). Never invent URLs. If a fact can't be confirmed, mark it (`confidence: "medium"`, or empty `links` for channels, which the page shows as "unconfirmed").
- The pipeline must stay zero-token: no AI calls at runtime, standard library only.

## Layout
- `data/curated/`: hand-checked evidence, 91 sources, 32 channels, 55 projects and 80 people.
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

## Current state (as of 2026-10-13)
- The code is complete and committed locally, and all 15 offline tests pass.
- It has NOT been pushed yet: the GitHub repo `datazen123/triad-signal-atlas` has to be created (empty, public).
- The collectors have never run against the live APIs. The build environment had no internet, so they were tested only on fixtures shaped from the API docs. Verified live: Federal Register, Comtrade (for China as reporter), Wayback, PortWatch ArcGIS, World Bank. Docs only: OpenAlex, Nobel v2.1, CelesTrak. OFAC failed entirely and was not built.
- The live panels on the page show "pending" until the first workflow run.

## Next steps, in order
1. Create the GitHub repo, push `main`, set Settings → Pages → Source to "GitHub Actions", and set Actions workflow permissions to read/write.
2. Run `python pipeline/doctor.py --force` locally (with internet) or trigger the workflow with force. Fix any collector whose real response shape differs from the fixtures, and update the fixtures to match.
3. In particular, check `undesa_migrants.py` header detection on the real 2024 xlsx, and the field paths in `nobel_bridges.py`.
4. Fill the 14 unconfirmed channels in `channels.json` with official primary links: US–CN Defense Telephone Link, Lima 2024 nuclear-control statement, S&T Agreement renewal, US–RU NRRC/launch notification, INCSEA, ISS seat swap, Istanbul embassy talks, CN–RU joint air patrols, naval and coast guard patrols, the 2009 launch-notification agreement (extension: Dec 2020 or 2021?), Tianwan 7/8 and Xudapu 3/4, local-currency settlement share, WMO, Cospas-Sarsat. Also replace the Sputnik-only source for MMCA 2026 and the Xinhua-only sources for New START, Ukraine talks and the NPT RevCon 2026 with official pages where possible.
5. Upgrade the 8 medium-confidence people and 13 medium-confidence projects to primary sources. Five people currently rely on Wikipedia mirrors or news sites: Pei, Kissinger, Leonov, Rostropovich, Yau.
6. Optional: add the SMTP secrets for direct email alerts, and a `CONTACT_EMAIL` secret for OpenAlex's polite pool.
7. After a successful run, republish `site/index.html` to the claude.ai artifact above so the snapshot shows live data.

## Conventions
- After editing the template or data, run `python pipeline/build.py`, then syntax-check the embedded script before committing:

  ```
  sed -n '/<script>/,/<\/script>/p' site/index.html | sed '1d;$d' > /tmp/c.js && node --check /tmp/c.js
  ```

- Commit messages end with the co-author lines used in the git history.
