# Triad Signal Atlas

An evidence board for how the great powers actually relate. It covers the United States, China and Russia, with the EU, India, Japan and the UK in the second view. The board brings together:

- **91 primary sources** in a rotatable 3D constellation, ranked on an evidence ladder from physical sensors down to state media.
- **32 diplomatic and security channels**, each with its status and primary-source links shown on hover.
- **55 joint projects**, such as ISS, ITER, smallpox eradication, Megatons to Megawatts and the Rosetta Disk. They sit in a 3D "powers web" with a year slider.
- **80 documented bridge-builders**: scientists, envoys, doctors, artists and religious figures who carried trust across borders. They feed a Bridge Index matrix.
- **Live data** that refreshes itself: research co-authorship, mirror trade statistics, Entity List actions, satellites in orbit, chokepoint shipping, Nobel laureates who crossed borders, and migrant stock between powers.

The page is one self-contained HTML file: `site/index.html`.

## How it updates without anyone spending tokens

A GitHub Actions workflow (`.github/workflows/update.yml`) runs daily at 06:17 UTC. No AI model is involved.

1. **Self-test.** It first runs offline unit tests (`pipeline/tests/`). A failure here means our own code broke, not an upstream API.
2. **Collect.** `pipeline/doctor.py` runs each collector that is due:

   | Collector | Source | Runs every |
   |---|---|---|
   | `openalex` | OpenAlex API: co-authored papers per pair of powers per year | 7 days |
   | `nobel` | Nobel Foundation API: laureates born in one power who did the prize work in another | 30 days |
   | `fedreg` | Federal Register API: Commerce Department Entity List documents naming China or Russia | 3 days |
   | `comtrade` | UN Comtrade public API: US/China/Russia trade, reported by both sides | 30 days |
   | `portwatch` | IMF PortWatch ArcGIS service: weekly chokepoint transits | 7 days |
   | `satcat` | CelesTrak SATCAT: active satellites and launches by owner | 7 days |
   | `migrants` | UN DESA International Migrant Stock workbook | 30 days |
   | `links` | Every evidence URL in the curated data | 7 days |

3. **Build.** `pipeline/build.py` embeds curated data, live data and health into `template/atlas.html` and writes `site/index.html`.
4. **Publish.** The refreshed data is committed and the site is deployed to GitHub Pages.
5. **Alert.** `pipeline/notify.py` alerts you only when something stays broken.

### Self-diagnosis and self-repair

Each layer below is ordinary code with no AI and no tokens:

| Problem | What the pipeline does by itself |
|---|---|
| Timeouts, rate limits, 5xx errors | Retries with exponential backoff and jitter, and honours `Retry-After`. |
| An API changes its URL or filter syntax | Tries the alternative spellings each collector lists (`try_variants`). |
| An API returns nonsense (empty, a sudden 35% jump in history) | Validation rejects it and quarantines it in `data/live/quarantine/`. The page keeps the last good data. |
| A source stays down | A circuit breaker drops it to weekly attempts. The page shows the data's age and marks it stale. |
| An evidence link dies (404 twice in a row) | Swaps in the closest Internet Archive snapshot, labelled "archived copy". It reverts automatically if the original returns. |
| A government site blocks bots (403) | Marked "unverifiable", not dead, so working links aren't replaced. |
| A site times out or drops foreign traffic | Marked "unreachable", not dead; only real 404/410 answers trigger an archived copy. |
| A third-party package breaks | Can't happen: the pipeline uses only the Python standard library. |
| One collector crashes | It is isolated. The others still run and the site still builds. |

### How you get told

- **GitHub issue.** After 2 consecutive failures, or when data goes stale, the bot opens an issue labelled `pipeline-health` that @mentions you, so GitHub emails you. It comments only when the set of problems changes, and closes the issue itself after the next clean run.
- **GitHub's own email.** Workflow failures also trigger GitHub's built-in notification. Check that Settings → Notifications → Actions is on.
- **Direct email (optional).** Add these repository secrets and every alert also goes straight to your inbox over SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `ALERT_TO`. For Gmail, use `smtp.gmail.com`, port `465` and an app password.

## One-time setup

1. Push this folder to `github.com/<you>/triad-signal-atlas`.
2. **Settings → Pages → Source: GitHub Actions.** The workflow also tries to enable this itself.
3. **Settings → Actions → General → Workflow permissions: Read and write.**
4. Optional: add the SMTP secrets above, and `CONTACT_EMAIL` to join OpenAlex's faster "polite pool".
5. **Actions → Update atlas → Run workflow**, with "force" ticked, for the first full collection.

## Run locally

```bash
python -m unittest discover -s pipeline/tests -v   # offline tests
python pipeline/doctor.py --force                  # collect everything now
python pipeline/doctor.py --only openalex          # one collector
python pipeline/build.py                           # writes site/index.html
```

## Editing the evidence

The curated data lives in `data/curated/`:

| File | Contents |
|---|---|
| `sources.json` | The 91 sources: evidence class, coverage, what to watch, bias. |
| `channels.json` | Bilateral and trilateral channels, with status, as-of date and primary links. Entries with empty `links` show as "unconfirmed". |
| `projects.json` | Joint projects: years, member powers, measured outcome, source, confidence. |
| `people.json` | Bridge-builders: origin, where they worked, field, the specific contribution, source, caveat. |

Every entry needs a source URL; the tests enforce this. Pushing a change rebuilds the site.

## Adding a collector

Write a module in `pipeline/collectors/` with these attributes:

- `NAME`, `TITLE`, `EVERY_DAYS`, `SOURCE_URL`
- `collect(prev) -> dict`
- `validate(payload, prev) -> list[str]`

Add the module to `collectors/__init__.py` and add a fixture in the tests. `pipeline/API_NOTES.md` records what was verified about each upstream API.
