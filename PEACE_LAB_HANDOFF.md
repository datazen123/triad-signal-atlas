# Peace Lab handoff (from claude.ai session, 2026-10-13)

Continue this in Claude Code. Read `CLAUDE.md` first for the atlas, pipeline and the owner's preferences. This file captures the owner's requests about the **Peace Lab** and all the design work done so far. **Nothing in Peace Lab has been built yet.** The repo as of `7fecd43` is healthy: all 8 collectors are live, last run 2026-10-12.

## The owner's requests, verbatim

**1. Original Peace Lab request**
> Enrich our artifact: Need to visualize all possible angles approaches technologies methods etc of an mvp that would foster cultivate and sustain and develop towards world peace. Make us a 3d shape shifting and rotatable and something I can play with to stimulate ideas conduct thought experiments, philosophize, and contemplate (extend exercises for me off screen off device for a continuous integration process of creation)

**2. Addition**
> Among MVP approaches: "news de-bias-er" / "allow me to form my own opinion" should be added and see what other novel approaches you can triangulate and think out loud virtually with me

**3. Latest direction**
> status on Peace Lab and MVP design-approach 3d ideator? it should work in artifact, and more importantly in the deployment you have here: https://datazen123.github.io/triad-signal-atlas/ — its for me and anyone interested (I want to do a proper launch when ready). i don't want to lock into 2-3 approaches.. can we try them all in an immersive un-noticeable delay way?

**4. Process preference**
> you're asking too much for permissions to fetch web pages

Keep web fetching to a minimum and batch it. Use Chinese-language search queries and report in English. Prefer primary, official and peer-reviewed sources.

## Hard requirements

- **Both targets.** It must work on GitHub Pages (`site/index.html`) and as a claude.ai artifact.
  - On Pages there is no `window.claude`, so everything must work as plain HTML/JS.
  - In the artifact there is a strict content-security policy: scripts only from cdnjs, jsdelivr/npm or unpkg, and no fetch to other hosts. The current page uses no libraries; keep it that way.
- **Launch-ready.**
  - `build.py` currently writes the template as-is. That has no `<!doctype html>` and no viewport meta, so **the Pages site renders in quirks mode, and phones won't scale it correctly**.
  - Fix: have `build.py` wrap `site/index.html` in a full document (doctype, charset, `viewport` with `viewport-fit=cover`, meta description, Open Graph tags).
  - Keep an unwrapped copy (e.g. `site/artifact.html`) for publishing to the artifact, because the artifact adds its own skeleton.
- **All approaches, no shortlist.** Every one gets an instant, client-side mini-prototype.
- **No noticeable delay.** No network calls in Peace Lab. Everything is precomputed or computed in-browser. Morphs run on requestAnimationFrame. Panels render on demand.
- **Zero-token at runtime.** The page can work without the `sample` capability. Only an optional "Deepen with Claude" button may use it, hidden when `claude.use('sample')` is null.
- **Evidence discipline.** Every node needs a source URL; extend the tests to `data/curated/peace.json`. Mark unverified ones `"conf": "check"`, and show a "check source" flag on the card until each is verified. Never invent URLs.

## Design (agreed direction; build this)

New section **Peace Lab**, placed right after the header and first in the nav. Data goes in `data/curated/peace.json`; `build.py` adds it to the embedded `ATLAS` data.

### 3D shape-shifting ideator

- Reuse the `Orbit` class in `template/atlas.html`.
- Around 70 "approach" nodes, coloured by domain and sized by evidence confidence.
- **Lenses.** Each lens is a target position set; morph between them with eased interpolation (~1.2 s, interruptible mid-morph):
  - **Globe:** Fibonacci sphere, with domains forming bands.
  - **Lotus:** one petal per domain; opens and closes.
  - **Torus of practice:** major angle = phase (foster → cultivate → sustain → develop), minor angle = scale.
  - **Spiral of time:** helix, with height = horizon (now → years → decades → generations).
  - **Ladder of scale:** stacked rings: self → relation → community → nation → world.
  - **Lattice:** labelled axes: X = domain, Y = scale, Z = horizon.
- **Shake:** scatter randomly, then settle back. A brainstorming jolt.
- **Breathe:** the whole form pulses at about 5.5 breaths per minute, with "in / out" text. Used by Contemplate.
- **Threads:** when a node is selected, draw edges to nodes that share a tag. A toggle shows all threads faintly.
- Hover a node for its evidence card (reuse the global `#card` and `cardFor`). Tap or click to pin it and open its **Play** panel.

### Node schema

```
{id, name, domain, scale, phase, horizon, tags[], what, why, mvp, q, play:{engine, params}, src, url, conf}
```

- **domain:** mind | relation | culture | economy | institution | security | technology | ecology | information
  - `information` is new, for the de-biaser family.
- **scale:** self | relation | community | nation | world
- **phase:** foster | cultivate | sustain | develop
- **horizon:** now | years | decades | generations

### Side panel tabs

Play · Collide · Compose MVP · Contemplate · Practices (off-screen) · Journal

### Play engines

Every node maps to one engine with parameters. All run instantly in the browser.

1. **`reflect`**: a prompt and a textarea; saves to the journal. Used by most philosophical nodes.
2. **`debias`**: the **news de-biaser / "form my own opinion"**.
   - **Write first.** You write your take *before* any analysis is shown, to avoid anchoring.
   - **Paste.** Paste 2–3 versions of a story.
   - **Highlight.** The page marks loaded words (from a lexicon), unattributed claims ("sources say", "reportedly"), numbers, quotes and named entities.
   - **Omission diff.** Sentences or facts in one version that are absent from the others, using content-word Jaccard overlap.
   - **Claim ladder.** Tags each claim with its evidence rung (A–F, reusing `EV`).
   - **Revisit.** Ends with a "did your view change, harden, or gain nuance?" step.
   - A **mirror-headlines** mode compares tone for the same event across outlets.
   - The "Load sample" button must use clearly labelled **made-up** example texts. No fabricated quotes from real people.
3. **`dilemma`**: iterated prisoner's dilemma against tit-for-tat, always-defect, grudger, random and generous tit-for-tat. You play 10 rounds, or run Axelrod's tournament automatically. A stag-hunt variant comes via params.
4. **`itt`**: the ideological Turing test. Pick a contested topic, write the other side's view, and check it against a self-rubric: their values, fears, best evidence, "would they nod?". A copy button lets you send it to a real person from that side ("perspective-getting").
5. **`grit`**: a trust ledger based on Osgood's GRIT. Log small unilateral steps and whether they were reciprocated. A tension meter falls with each reciprocated step. Stored in `localStorage`.
6. **`fermi`**: slider estimators, e.g. "how many people do peace work today, and what would double it?", or the cost of violence against spending on peace.
7. **`breathe`**: a contemplation timer (3, 5 or 10 minutes) that drives the Breathe morph. At the end it prompts one journal line.
8. **`premortem`**: pick two powers and a flashpoint, walk the escalation ladder step by step, and set a tripwire plus an off-ramp at each step. It outputs a pre-mortem summary.
9. **`words`**: the word "peace" across languages, with literal meanings. Verify each:
   - 和平 hépíng (Chinese)
   - 平和 heiwa (Japanese)
   - 평화 pyeonghwa (Korean)
   - мир mir (Russian; means both "peace" and "world")
   - शांति shānti (Hindi/Sanskrit)
   - سلام salām (Arabic)
   - שלום shalom (Hebrew)
   - Frieden (German)
   - pax (Latin)
10. **`veil`**: veil of ignorance. Design rules for the US–China–Russia relationship, then get assigned at random to a country and role, and reflect.
11. **`provenance`**: an opinion-provenance journal. Enter a strongly held view, pick where it came from (which rung A–F), and see a chart of your own views by rung.
12. **`superordinate`**: a "shared problems" market of problems no single power can solve alone, such as planetary defense, pandemic early warning, AI safety evaluations and Arctic search and rescue. Each lists the powers it needs. Draft the smallest joint step.
13. **`slow`**: slow news. Save a headline and your take now. After 7 days, the page shows it as due so you can compare what you thought then with what turned out to be true.
14. **`bridge`**: write a statement both sides could sign. It's checked for loaded words and shared-value words, as in Pol.is or Community Notes "bridging".

### Global tools

- **Collide:** pick the selected node plus a random node from another domain. The two pulse in 3D, and a "What if A met B?" card shows a generated thought experiment and an exercise.
- **Compose MVP:** add up to 5 nodes to a tray, which generates an MVP canvas:
  - mechanism
  - smallest test
  - phase-coverage bar across the four phases
  - scale span
  - evidence to read
  - risks: per tag, e.g. contact under unequal status can backfire (Allport's conditions); "show the other side" can polarize (Bail et al. 2018)
  - a metric to watch
  - a save-to-journal button
- **Contemplate:** a slow rotation with a breathing overlay, one question on screen, and a timer.
- **Thought-experiment deck** (16 cards, each with a setup and three questions):
  1. veil of ignorance
  2. stag hunt
  3. iterated prisoner's dilemma: what does "forgiving" mean for nations?
  4. Robbers Cave: what's today's broken water tank?
  5. overview effect for leaders
  6. leaders who swapped childhoods
  7. мир = peace = world
  8. a 1000-year audit
  9. Ship of Theseus for treaties
  10. harmony without uniformity: an orchestra where no two instruments share a melody
  11. Galtung's inversion: if wars stopped tomorrow, what violence would remain?
  12. Kant's universal hospitality
  13. a zero-sum audit
  14. the empty chair: future generations and other species
  15. the smallest verifiable promise
  16. a Fermi estimate of peace work

### Off-screen practices and the "continuous integration" creation loop

- **The loop:** an SVG ring of Notice → Ponder → Combine → Make → Test → Share → Reflect. Each stage has an on-device action and an off-device action.
- **Practices by cadence:**
  - **Daily:** a minute of silence at a fixed time; one word for "peace" in another language; steelman an opposing view while walking.
  - **Weekly:** a meal or call across borders or politics, asking "what do you fear, what do you hope?"; make something that combines two traditions (e.g. a melody in a pentatonic scale over a Russian minor progression); trace one object's supply chain across the powers.
  - **Monthly:** a letter you won't send, to a leader of another country; run one small test from Compose MVP; visit a place of memory.
  - **Yearly:** review the journal, re-rank the nodes, publish one piece.
- "Today's practice" is picked deterministically from the date.
- **Pocket card export:** this week's practices plus the chosen nodes, as `.md`.

### Journal storage (works on both targets)

- `localStorage` key `peacelab.journal.v1`, with try/catch around every read and write. Tell the viewer "Saved in this browser — export to keep it."
- Export as Markdown:
  - **On Pages:** a Blob plus an `<a download>` link.
  - **In the artifact:** `await claude.use('downloads')`, then `downloads.save({filename, data})`, and publish the artifact with `capabilities: {downloads: true}`. If it's null, fall back to Copy.
- Optional later: the `db` capability at `db.collection('data/users/'+uid).doc(id)` for durable private notes in the artifact.

## Approach nodes drafted (~70; sources still to be verified)

Format: `id`: domain / scale / phase / horizon · engine · source (draft).

**Mind**
- `compassion`: self / cultivate / now · breathe · Weng et al. 2013, Psych Sci, doi 10.1177/0956797612469537
- `deep-canvass`: relation / foster / now · itt · Broockman & Kalla 2016, Science, doi 10.1126/science.aad9713
- `perspective-getting`: relation / foster / now · itt · Eyal, Steffel & Epley 2018, JPSP (find DOI)
- `humility`: self / cultivate / now · provenance · Leary et al. 2017, PSPB, doi 10.1177/0146167217697695
- `overview`: world / foster / generations · reflect · Yaden et al. 2016, doi 10.1037/cns0000086
- `metta`: self / cultivate / now · breathe · Karaniya Metta Sutta (accesstoinsight.org)

**Relationship**
- `contact`: community / foster / years · reflect · Pettigrew & Tropp 2006, doi 10.1037/0022-3514.90.5.751
- `robbers-cave`: community / foster / now · superordinate · psychclassics.yorku.ca/Sherif
- `nvc`: relation / cultivate / now · reflect · cnvc.org
- `exchange`: nation / cultivate / decades · reflect · Fulbright
- `sistercities`: community / sustain / decades · reflect · sistercities.org
- `sustained-dialogue`: community / sustain / years · itt · sustaineddialogue.org (Dartmouth Conference)
- `track2`: nation / foster / years · premortem · Pugwash, Nobel 1995
- `restorative`: community / sustain / years · reflect · UNODC handbook
- `virtual-exchange`: relation / cultivate / years · itt · Soliya

**Culture**
- `music`: community / cultivate / years · reflect · West-Eastern Divan Orchestra
- `sport`: nation / foster / now · reflect · Olympic Truce
- `harmony`: world / develop / generations · reflect · Analects 13.23 (ctext.org)
- `ubuntu`: community / cultivate / generations · reflect
- `ahimsa`: world / foster / generations · reflect · mkgandhi.org
- `hongik`: world / develop / generations · reflect · Korea Framework Act on Education, Art. 2
- `mir`: world / foster / generations · words
- `galtung`: world / develop / generations · reflect · doi 10.1177/002234336900600301
- `peace-ed`: nation / cultivate / decades · reflect · UNESCO 2023 Recommendation
- `longnow`: world / develop / generations · reflect · longnow.org
- `memory`: world / sustain / generations · reflect · Hiroshima Peace Memorial Museum

**Economy**
- `interdependence`: nation / sustain / decades · reflect · Farrell & Newman 2019, doi 10.1162/isec_a_00351 (the evidence is mixed: show both sides)
- `shared-infra`: world / develop / decades · superordinate · Indus Waters Treaty (and its 2025 abeyance)
- `cost-of-violence`: world / develop / years · fermi · IEP Global Peace Index
- `commons`: community / sustain / generations · reflect · Ostrom, Nobel 2009

**Institution**
- `mediation`: nation / foster / now · premortem · peacemaker.un.org
- `women-peace`: nation / sustain / years · reflect · UN Women Global Study 2015
- `pbc`: world / sustain / decades · reflect · UN Peacebuilding Commission
- `icj`: world / sustain / generations · reflect · icj-cij.org
- `assembly`: nation / develop / years · bridge · Ireland's Citizens' Assembly
- `trc`: nation / sustain / decades · reflect · justice.gov.za/trc
- `kant`: world / develop / generations · veil · Perpetual Peace (Gutenberg)
- `rawls`: world / develop / generations · veil · A Theory of Justice

**Security**
- `cbm`: nation / foster / now · grit · OSCE Vienna Document
- `grit`: nation / foster / years · grit · Osgood 1962; JFK "Strategy of Peace", 1963
- `arms-verif`: world / sustain / decades · reflect · INF, 2,692 missiles
- `hotline`: world / foster / now · premortem · 1963 Hotline MOU
- `peacekeeping`: nation / sustain / years · fermi · Hultman, Kathman & Shannon 2013, doi 10.1111/ajps.12036
- `ddr`: community / sustain / years · reflect · UN DDR
- `demining`: community / sustain / decades · reflect · Mine Ban Convention (note the 2025 withdrawals)
- `civil-resistance`: nation / develop / years · reflect · Chenoweth & Stephan
- `war-premortem`: nation / foster / now · premortem · Track 1.5 tabletop exercises
- `axelrod`: world / cultivate / years · dilemma · doi 10.1126/science.7466396
- `stag-hunt`: world / foster / years · dilemma (stag) · Stanford Encyclopedia of Philosophy

**Technology**
- `early-warning`: world / foster / now · reflect · ViEWS (viewsforecasting.org)
- `osint-verif`: world / sustain / now · reflect · Copernicus
- `bridging-ranking`: world / develop / years · bridge · Community Notes docs; Pol.is (compdemocracy.org)
- `translation`: world / cultivate / years · words · Meta NLLB-200
- `ai-safety`: world / develop / years · superordinate · Bletchley Declaration (gov.uk)
- `cyber-norms`: world / sustain / years · grit · UN GGE 11 norms
- `open-gov`: nation / sustain / years · reflect · Open Government Partnership
- `sesame`: world / develop / decades · superordinate · sesame.org.jo
- `big-science`: world / develop / generations · superordinate · CERN
- `planetary-defense`: world / develop / decades · superordinate · NASA DART, IAWN

**Ecology**
- `peace-parks`: nation / sustain / decades · reflect · peaceparks.org
- `climate`: world / develop / generations · superordinate · Paris Agreement
- `antarctic`: world / sustain / generations · reflect · ats.aq
- `env-peace`: community / foster / years · reflect · Environmental Peacebuilding Association / UNEP
- `seedvault`: world / sustain / generations · reflect · seedvault.no (ICARDA's 2015 withdrawal)
- `disaster-dipl`: nation / foster / now · reflect · the 1999 Greece–Turkey earthquakes
- `health-bridge`: world / sustain / decades · reflect · WHO smallpox eradication; vaccination "days of tranquility"

**Information** (the de-biaser family the owner asked for)
- `debiaser`: self / foster / now · debias · prebunking (Roozenbeek et al. 2022, Sci Adv); lateral reading (Wineburg & McGrew 2019); note the backfire risk (Bail et al. 2018, PNAS)
- `accuracy-nudge`: self / cultivate / now · debias · Pennycook et al. 2021, Nature
- `mirror-headlines`: world / sustain / years · debias (mirror mode)
- `domestic-news`: relation / cultivate / now · words or reflect · read each country's own domestic news, translated
- `slow-news`: self / sustain / now · slow
- `provenance`: self / cultivate / now · provenance
- `itt-game`: relation / foster / now · itt · Caplan 2011 ("ideological Turing test")
- `omission-diff`: nation / foster / now · debias
- `trust-ledger`: community / sustain / years · grit

## Citations to verify (batch them; minimise fetches)

Every `url` above is a draft from memory. Verify in one batched pass, or mark `"conf":"check"` and let the weekly `links` collector flag dead ones. The automated link check runs in GitHub Actions without anyone approving fetches, so it's the cheapest verifier for "does the page load". A human or Claude pass is still needed for "does it support the claim".

Highest priority: the numeric claims.
- Pettigrew & Tropp: 515 studies
- Women in peace processes: 35% more likely to last 15 years
- INF: 2,692 missiles
- Chenoweth & Stephan: about twice as often
- Hultman et al.
- Pennycook et al.
- Roozenbeek et al.
- Bail et al.

## Repo and push status

- The claude.ai session cloned `datazen123/triad-signal-atlas` to `/home/claude/remote-atlas`, but its **pushes are refused**: the Claude GitHub App isn't linked for this account. Claude Code on the owner's machine pushes normally.
- claude.ai artifact (static snapshot): https://claude.ai/artifact/3gN2WL2M1QJLGAS7r1Wqr9
  - After building, publish an unwrapped `site/artifact.html` there with `capabilities: {downloads: true}`.

## Suggested order of work

1. Fix `build.py`: wrap the Pages output in a proper document head (doctype, viewport, Open Graph). Keep the unwrapped artifact copy.
2. Write `data/curated/peace.json`: nodes, the 16 thought experiments and the practices. Extend the tests.
3. Build the Peace Lab section in `template/atlas.html`: lenses and morphs, then the 14 engines, then Collide, Compose, Contemplate, Practices and Journal.
4. Check rendering with Playwright: no console errors, no horizontal overflow at 400px, 60fps morphs.
5. Push and let Actions deploy, then republish the artifact.
6. Verify citations in one batched pass, then prepare for the launch.
