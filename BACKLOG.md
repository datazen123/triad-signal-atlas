# Backlog: Common Ground Atlas

Future versions, roughly in order. Nothing here is built yet. Data sources listed below are **unverified candidates**: check each one's own site, licence and method before any of it enters `data/curated/`, and follow the usual rule (every entry has a primary source URL; nothing is invented).

## v3: All peoples, not just states

### Why
The atlas began with three states and now covers seven powers. But most of the world's relationships are not between states. Many people have no state that speaks for them, or live across several. A peace tool that only shows flags repeats the very map that leaves them out. This version gives every people space to be seen, to connect, and to build relationships with everyone else, including with the powers already in the atlas.

### Who it should include
- **Stateless nations**: peoples with a shared identity and homeland but no state of their own.
- **Indigenous peoples**: including those inside the seven powers already in the atlas.
- **Diasporas**: communities living outside a homeland, often bridging two or more places.
- **Refugees and displaced people**: people forced from home, across a border or within their own country.
- **Unrecognised or partially recognised territories**: places with their own institutions whose status is disputed.
- **Minorities within states**: linguistic, religious and ethnic minorities.
- **Stateless individuals**: people no state recognises as nationals.

### UX principles (how to add them without overwhelming)
- **People-first, not flag-first.**
  - The entry point is "who are you looking for?" or "who would you like to meet?", not a map of borders.
  - Peoples appear as constellations of communities, languages and places, not as shaded territory.
- **Self-identification first.**
  - Each people is named the way it names itself, with its endonym first and exonyms second.
  - Sources from the community itself (its own councils, organisations and media) sit alongside outside sources, and are labelled as such.
  - Allow more than one identity per person or community; diasporas and mixed heritage are normal.
- **The tool makes no recognition claim.**
  - Showing a people, territory or government is never a statement about sovereignty or legal status.
  - Disputed status is shown as "recognised by X, not by Y", with sources, never as a verdict.
  - A short standing note says this on every relevant card.
- **Layers you can toggle.**
  - Off by default at first, then a gentle "there is more here" prompt.
  - Separate toggles: states and powers · peoples and nations · diasporas · displaced people · territories.
  - Each layer has a count and a one-line explanation before it is switched on.
- **Progressive disclosure.**
  - Start with a few relationships the viewer already cares about, then widen.
  - Use the dome scheduler (as in Peace Lab v2) so small peoples are not buried under large ones over time.
- **Dignity and safety.**
  - No precise locations for vulnerable communities. Aggregate to region level.
  - No individual names of refugees or minors. Bridge people only with their documented public role and consent where possible.
  - A takedown and correction route for communities who object to how they are shown.
- **Connection, dialogue, relationship-building.**
  - Bridges across divides: documented moments of help, rescue, shared culture and dialogue between a people and others.
  - Dialogue prompts written with, not about, the people concerned.
  - Peace Lab approaches that apply (for example contact, joint problem-solving, shared language learning) linked from each people's card.
- **Language.**
  - Names in their own script, with romanisation.
  - Neutral, descriptive wording; no terms one side uses as slurs.

### Data-source candidates (all unverified)
Check existence, current URL, licence, update cadence and method before use. Prefer the community's own organisations and intergovernmental or academic sources.

| Candidate | Might give | Status |
|---|---|---|
| UNHCR refugee statistics (Refugee Data Finder) | refugees, asylum seekers, stateless people by origin and host | unverified |
| Internal Displacement Monitoring Centre (IDMC) | internally displaced people by country and cause | unverified |
| IOM Displacement Tracking Matrix | displacement at sub-national level | unverified |
| UN DESA International Migrant Stock (already used by the `migrants` collector) | diasporas between countries | in use for the seven powers; extend |
| UN Permanent Forum on Indigenous Issues, UNDRIP | Indigenous peoples' framework and reports | unverified |
| IWGIA, "The Indigenous World" yearbook | country-by-country Indigenous situation | unverified |
| Minority Rights Group, World Directory of Minorities and Indigenous Peoples | minorities and Indigenous peoples by country | unverified |
| Unrepresented Nations and Peoples Organization (UNPO) | self-described members: stateless nations, territories | unverified; membership is self-selected |
| ETH Zurich, Ethnic Power Relations (EPR) dataset | politically relevant ethnic groups and their access to power | unverified |
| Glottolog | languages and their relationships | unverified |
| Native Land Digital | Indigenous territories, languages and treaties as described by communities | unverified; contested boundaries by design |
| ILO Convention 169 ratifications | which states recognise Indigenous rights under this treaty | unverified |

### Open questions
- Who reviews entries for a people? A community advisory group, and how is it chosen?
- How do we show a people that spans several powers without implying it belongs to any of them?
- What is the smallest version worth shipping? Perhaps: displaced people and diasporas for the seven powers already in the atlas, from UN data, with a people-first card.
