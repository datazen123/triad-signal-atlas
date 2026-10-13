# Research log: channels and sources for all seven powers

Branch `research/all-powers` (2026-10-13). It covers `data/curated/channels.json` and `data/curated/sources.json`. The work builds on PR #1 (`research/primary-sources`) and supersedes it.

## Method

- Scope: the seven powers in `template/atlas.html` `POWERS` (US, UK, EU, RU, IN, CN, JP), which give 21 dyads. The 3 triad dyads were already covered, so this pass added the other 18.
- Evidence rule for channel status:
  - Only government pages count: foreign ministries, leaders' offices, defence ministries, treaty series, official legal portals, EU institutions and the CJEU.
  - Every URL in the data was fetched in this session, with a stdlib `urllib` client, `curl` or WebFetch.
  - Pages that blocked bots are named in the entry's `note`.
- Searches were run in English, Chinese (外交部, 商务部 pages), Japanese (防衛省, 水産庁, 外務省 queries) and Russian (Kremlin, pravo.gov.ru, MID queries). All reporting is in English.
- Dyad strings:
  - New dyads use the existing `"A–B"` en-dash form, with codes in `POWERS` order: `US–UK`, `US–EU`, `US–IN`, `US–JP`, `UK–EU`, `UK–RU`, `UK–IN`, `UK–CN`, `UK–JP`, `EU–RU`, `EU–IN`, `EU–CN`, `EU–JP`, `RU–IN`, `RU–JP`, `IN–CN`, `IN–JP`, `CN–JP`.
  - The three existing triad dyads keep their strings, including `CN–RU`.
  - A template should match dyads order-insensitively.
- Status vocabulary is unchanged: `active`, `limited`, `dormant`, `ended`, `contested`.
  - "Suspended" relationships, such as EU–Russia dialogues, Japan–Russia peace talks and the EU–Russia visa facilitation agreement, are marked `dormant`. Their `desc` says "suspended".
- Multilateral `all_*` entries:
  - They keep `dyad: "All three"`, so the current template still renders them.
  - Each now has an optional `members` array listing which of the seven belong.
  - Their `desc` adds the UK, EU, India and Japan where relevant.
  - A template change could relabel the tab, for example to "All".

## Channels added (44)

| Dyad | Channels (status) |
|---|---|
| US–UK | Mutual Defence Agreement 1958 and 2024 amendment (active); Technology Prosperity Deal (limited) |
| US–EU | Reciprocal trade framework, Aug 2025 (active); Trade and Technology Council (dormant); Data Privacy Framework (active) |
| US–IN | 10-year Major Defense Partnership framework (active); Interim trade agreement framework (active) |
| US–JP | Leader summits (active); trade and $550bn investment framework (active); critical minerals framework (active) |
| UK–EU | Summits and Security and Defence Partnership (active); WA Joint Committee and TCA Partnership Council (active) |
| UK–RU | Diplomatic channel with expulsions (limited); 1986 INCSEA (limited, current use unconfirmed); sanctions regime (contested) |
| UK–IN | CETA, in force 15 Jul 2026 (active); Technology Security Initiative (active) |
| UK–CN | Leader talks, Jan 2026 (active); Economic and Financial Dialogue and Financial Working Group (active) |
| UK–JP | Reciprocal Access Agreement (active); GCAP International Government Organisation (active) |
| EU–RU | Summits and PCA dialogues (dormant); visa facilitation agreement (dormant, suspended); sanctions packages (contested) |
| EU–IN | FTA, concluded 27 Jan 2026 (active); Trade and Technology Council (active) |
| EU–CN | Summits (limited); Trade and Investment Consultations (active); High-level Strategic Dialogue (active) |
| EU–JP | Summits and Competitiveness Alliance (active); Security and Defence Partnership (active) |
| RU–IN | Annual summits (active); reciprocal logistics agreement (RELOS) (active) |
| RU–JP | Peace treaty talks (dormant, suspended by Russia in 2022); fisheries commissions (active) |
| IN–CN | Special Representatives talks (active); WMCC (active); leader meetings and normalisation (active) |
| IN–JP | Annual summits (active); defence ministers' dialogue and 2+2 (active) |
| CN–JP | Maritime and Aerial Communication Mechanism and hotline (limited); High-level Consultation on Maritime Affairs (dormant); leader and ministerial contact (contested); seafood import suspension (contested) |

## Unconfirmed or partly confirmed (see each `note`)

- `usuk_tpd`: The Dec 2025 US pause and the reported Jan 2026 re-opening of the nuclear pillar are not confirmed from a primary page.
  - The Commons committee report returned HTTP 403.
  - The gov.uk copy of the MOU returned 404.
- `usin_trade`: The tariff figures come from the White House fact sheet, which was not fetched. Whether the Interim Agreement has been signed is unknown.
- `ukru_incsea`: It is unknown whether the INCSEA talks have met since 2022, or whether the 2021 protocol is in force.
- `eucn_summit`: That there is no 2026 summit date comes only from a Commission briefing video listing.
- `ruin_summit` and `ruin_relos`: The 24th summit in 2026 and India's ratification of RELOS are unconfirmed.
- `cnjp_mamc`: Hotline use since the Nov 2025 rupture is unconfirmed.
- `cnjp_maritime`: It is marked dormant only because Japan's 2026 white paper lists no round after Oct 2024.
- `cnjp_seafood`: No GACC customs notice was fetched, and it is unknown whether imports have resumed.
- `incn_wmcc`: The 35th WMCC (May 2026) is from an Indian embassy PDF whose URL returned 404.
- `all_p5`, `all_iaea` and `all_nptrevcon`: Membership across the seven is background knowledge.
  - iaea.org returned 403 or 402.
  - UNODA returned a 202 bot challenge.
- No channel was left with empty `links`. Every new entry has at least one fetched official page confirming the channel and its latest event. Where current status goes beyond that, the gap is stated in the note.

## Dead ends and blocked sites

- **mofa.go.jp** (Japan MOFA) returned HTTP 403 (Akamai "Access Denied") to `urllib`, `curl` and WebFetch on every page. Substitutes used instead:
  - Kantei (japan.kantei.go.jp)
  - Japan MOD PDFs and the white-paper CSV under `mod.go.jp/j/`
  - The Fisheries Agency (jfa.maff.go.jp)
  - Counterpart readouts
- **mod.go.jp**: The root page and `/en/` articles returned 403, but `/j/approach/...pdf` and `/j/press/wp/.../*.csv` returned 200.
- **mea.gov.in** (India MEA) returned 403 to every client. Substitutes: PIB (pib.gov.in), PM India (pmindia.gov.in), the PRC MFA and the Kremlin.
- **consilium.europa.eu** (EU Council) returned 403. The EEAS delegation copy of the 25th EU–China summit release was used instead.
- **EUR-Lex** returned HTTP 202 (a bot challenge), so the DG HOME page was used for the visa suspension.
- **ec.europa.eu/commission/presscorner/detail/...** renders with JavaScript. The same text was read from `presscorner/api/documents?reference=<REF>&language=en`, and the human URL is cited.
- **publications.parliament.uk** and **hansard.parliament.uk** returned 403.
- **media.defense.gov** and **war.gov** returned 403 for the US–India framework fact sheet.
- **mid.ru** serves a JavaScript bot challenge, so the Mar 2022 statement suspending the peace treaty talks was not read.
- **iaea.org** returned 403 or 402. **treaties.unoda.org** returned 202. **ctbto.org** returned 403.
  - For the CTBT, the UN Treaty Collection depositary page was used instead (200). It lists UK ratification on 6 Apr 1998, Japan on 8 Jul 1997, US, CN and RU as signatures only, and no India entry.
- **eoibeijing.gov.in**: The 35th WMCC PDF returned 404.
- **gov.uk** copy of the Technology Prosperity Deal MOU: 404.
- **Search-only claims not used:** search-engine summaries sometimes stated facts with no primary page behind them. Examples: the 18% US–India tariff, the "45-day rule" in the US–Japan MOU, and SAFE talks collapsing. These were left out or labelled as unconfirmed.

## Sources audit (`sources.json`)

- `cov` arrays were widened for 63 sources and none were narrowed. The checker asserts that no existing coverage was dropped. Codes follow `POWERS` order.
- The rules applied:
  - **Each power's own readouts** (Kremlin, PRC MFA, Russian MFA, State Dept) cover all seven. Readouts of talks with the UK, EU, India and Japan were among the pages fetched for channels.
  - **Global datasets** (Comtrade, IMF, BIS, WTO, WIPO, OpenAlex, satellite catalogues, FIRMS, ADS-B, Copernicus, Landsat, Worldview, Global Fishing Watch, Nature Index) cover all seven by their stated global scope.
    - Where the unit is a state rather than the EU, the EU is left out: UN DL voting, UNOOSA register, SIPRI, UNROCA, PRIS, CTBTO and IRIS.
  - **Membership bodies** take their member lists from fetched pages:
    - ITER: no UK.
    - NPFC: US, EU, RU, CN, JP.
    - Antarctic Treaty consultative parties: no EU.
    - WMO Regional Telecommunication Hubs: New Delhi, Tokyo and Exeter listed.
    - Cospas-Sarsat: UK MCA, ISRO and Japan Coast Guard listed; EU not listed.
    - CTBT via the UN Treaty Collection.
  - **Topic-specific sources** get only the powers they cover:
    - SIPRI Yearbook and the FAS Nuclear Notebook: the nuclear-armed states among the seven.
    - The Political Declaration on military AI: endorsers among the seven, kept alongside the original US/CN/RU coverage.
    - Japan Joint Staff: adds JP.
    - EU Sanctions Map: adds EU.
    - ISS: adds JP.
    - CREA: adds the EU, India and Japan as buyers of Russian fossil fuels.
- Some `cov` changes rely on the source's stated scope rather than a page fetched for that power. This applies to Pew, CCGA, Levada (EU), ETO, Epoch, Open Doors, TIC and USTR. Treat them as reasonable but not page-verified.
- 25 sources were added, using the existing fields and A–F evidence codes:
  - **UK:** FCDO and No 10 readouts (D), UK Treaty Series (C), ONS (B), Bank of England Database (B), Hansard (C; 403 to bots), UK Sanctions List (C).
  - **EU:** EEAS (D), Commission press corner (D), EUR-Lex (C; 202 to bots), Eurostat trade (B), ECB Data Portal (B), EP Legislative Observatory (C).
  - **India:** MEA (D; 403 to bots), PIB (D), TradeStat (B), RBI statistics (B), ISRO (D), Lok Sabha (C).
  - **Japan:** MOFA (D; 403 to bots), Kantei (D), MOF Trade Statistics (B), BOJ Time-Series (B), JAXA (D), Diet record search (C), Fisheries Agency (D).
- Pages that block bots were kept where they are the authoritative official source. The block is stated in the source's `cav`.

## Template dependency (not changed here; `template/atlas.html` is owned by another agent)

- **Source sky crash:** The current template places source stars using `corners` and `TRIAD`, which only have US, CN and RU. `corners[c].x` throws for UK, EU, IN or JP. With this data and the current template, the Source Constellation script will error until the template supports seven corners.
  - `site/index.html` built on this branch passes `node --check` (syntax), but it would fail at runtime in that section.
  - Merge this after, or together with, the seven-power template change.
- **Dyad tabs:** The `DYADS` list only has the triad dyads plus "All three". The 44 new channels are in the data but will not show until the template lists the new dyads.
- **Optional `members` field:** It can drive an "All seven / members" view for the multilateral rows.

## Validation and URL check (2026-10-13)

- `python3 -m unittest discover -s pipeline/tests`: 24 tests, OK.
- `python3 pipeline/build.py`: OK, and the embedded script passes `node --check`.
- Checker results:
  - channels = 76, sources = 116, schema errors = 0.
  - All ids are unique, all statuses are in the vocabulary, all dyad codes are in `POWERS`, and all `ev`, `topics` and `cov` values are valid.
- URL statuses across all 252 URLs in both files: 200 = 225, 403 = 16, 202 = 5, 412 = 1, ERR = 5.
  - Every URL added in this pass returns 200, except the four intentionally kept bot-blocking homepages: hansard (403), eurlex (202), mea (403) and mofaj (403).
  - The other non-200s are pre-existing entries. kremlin.ru and eng.mil.ru gave transient TLS errors on this run, although kremlin.ru returned 200 earlier the same day.

### URL status table

| id | status | url |
|---|---|---|
| uscn_summits | 200 | https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202510/t20251030_11743847.shtml |
| uscn_summits | 200 | https://www.fmprc.gov.cn/mfa_eng/xw/zyxw/202605/t20260514_11910330.html |
| uscn_summits | 200 | https://www.mfa.gov.cn/gjhdq_676201/gj_676203/bmz_679954/1206_680528/xgxw_680534/202609/t20260925_12031134.shtml |
| uscn_mmca | 200 | http://eng.mod.gov.cn/2025xb/N/T/16464949.html |
| uscn_mmca | 200 | http://eng.mod.gov.cn/2025xb/N/T/16423311.html |
| uscn_dtl | 200 | https://www.govinfo.gov/app/details/GOVPUB-S-PURL-gpo34414 |
| uscn_dtl | 200 | http://eng.mod.gov.cn/xb/News_213114/TopStories/16408897.html |
| uscn_cn | 200 | https://www.whitehouse.gov/fact-sheets/2025/11/fact-sheet-president-donald-j-trump-strikes-deal-on-economic-and-trade-relations-with-china/ |
| uscn_cn | 200 | https://www.govinfo.gov/content/pkg/DCPD-202501078/html/DCPD-202501078.htm |
| uscn_ai | 200 | https://www.mfa.gov.cn/gjhdq_676201/gj_676203/bmz_679954/1206_680528/xgxw_680534/202609/t20260925_12031134.shtml |
| uscn_nc2 | 200 | https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/2024/11/16/readout-of-president-joe-bidens-meeting-with-president-xi-jinping-of-the-peoples-republic-of-china-3/ |
| uscn_nc2 | 200 | https://www.fmprc.gov.cn/mfa_eng/xw/zyxw/202411/t20241117_11527672.html |
| uscn_exportctl | 200 | https://www.whitehouse.gov/fact-sheets/2025/11/fact-sheet-president-donald-j-trump-strikes-deal-on-economic-and-trade-relations-with-china/ |
| uscn_exportctl | 200 | https://www.tid.gov.hk/en/tradecircular/files/2025/ci8892025a.pdf |
| uscn_exportctl | 200 | https://www.tid.gov.hk/en/tradecircular/files/2025/ci2025318a.pdf |
| uscn_sta | 200 | https://2021-2025.state.gov/amendment-and-extension-of-the-u-s-prc-science-and-technology-agreement-sta/ |
| uscn_sta | 200 | https://www.gov.cn/lianbo/bumen/202412/content_6992558.htm |
| usru_newstart | 200 | https://india.un.org/en/311310-un-secretary-general-statement-expiration-treaty-measures-further-reduction-and-limitation |
| usru_newstart | 200 | https://2021-2025.state.gov/u-s-countermeasures-in-response-to-russias-violations-of-the-new-start-treaty |
| usru_newstart | 200 | https://www.news.cn/world/20260205/74c3432ca6e445deab59a0da8cbf8616/c.html |
| usru_bmlna | 200 | https://2009-2017.state.gov/t/avc/trty/187150.htm |
| usru_bmlna | 200 | https://2021-2025.state.gov/history-of-the-national-and-nuclear-risk-reduction-center/ |
| usru_bmlna | 200 | https://2021-2025.state.gov/u-s-countermeasures-in-response-to-russias-violations-of-the-new-start-treaty |
| usru_incsea | 200 | https://2009-2017.state.gov/t/isn/4791.htm |
| usru_iss | 200 | https://www.nasa.gov/wp-content/uploads/2023/10/nac-oct2022-iss-final2.pdf |
| usru_iss | 200 | https://www.nasa.gov/news-release/nasa-shares-spacex-crew-14-assignments-for-space-station-mission/ |
| usru_ukraine | 200 | https://www.govinfo.gov/app/details/DCPD-202500855 |
| usru_ukraine | 200 | https://www.mofa.gov.ae/en/MediaHub/News/2026/1/23/UAE-Russia-Ukraine-United-States |
| usru_ukraine | 200 | https://www.mofa.gov.ae/en/MediaHub/News/2026/2/4/UAE-Tripartite-talks |
| usru_ukraine | 403 | https://www.eda.admin.ch/en/switzerland-is-committed-to-peace-in-ukraine |
| usru_ukraine | 200 | https://www.fmprc.gov.cn/mfa_eng/xw/zyxw/202605/t20260514_11910330.html |
| usru_ukraine | 200 | https://www.mfa.gov.cn/gjhdq_676201/gj_676203/bmz_679954/1206_680528/xgxw_680534/202609/t20260925_12031134.shtml |
| usru_embassy | 200 | https://ru.usembassy.gov/february-27-meeting-in-istanbul/ |
| usru_embassy | 200 | https://ru.usembassy.gov/april-10th-meeting-in-istanbul/ |
| usru_uranium | 200 | https://www.govinfo.gov/app/details/PLAW-118publ62 |
| cnru_airpatrol | 200 | http://eng.mod.gov.cn/2025xb/N/JE/16470142.html |
| cnru_airpatrol | 200 | http://eng.mod.gov.cn/2025xb/N/T/16426188.html |
| cnru_airpatrol | 200 | http://eng.mod.gov.cn/xb/News_213114/NewsRelease/16328897.html |
| cnru_naval | 200 | https://www.ccg.gov.cn/gjhz/202410/t20241017_2520.html |
| cnru_naval | 200 | http://eng.mod.gov.cn/2025xb/N/T/16473492.html |
| cnru_bmln | 200 | http://government.ru/announcements/42770/ |
| cnru_bmln | 200 | http://council.gov.ru/events/news/130890/ |
| cnru_pos | ERR URLError | https://www.gazprom.com/projects/power-of-siberia/ |
| cnru_nuclear | 200 | https://www.gov.cn/xinwen/2021-05/19/content_5608935.htm |
| cnru_nuclear | 200 | https://www.mee.gov.cn/xxgk2018/xxgk/xxgk09/202608/t20260813_1163971.html |
| cnru_nuclear | 200 | https://www.caea.gov.cn/n6760338/n6760342/c10768957/content.html |
| cnru_ilrs | 200 | https://www.cnsa.gov.cn/english/n6465668/n6465670/c6811967/content.html |
| cnru_ilrs | 200 | https://www.cnsa.gov.cn/english/n6465652/n6465653/c6812150/content.html |
| cnru_currency | 200 | http://government.ru/news/52428/ |
| usuk_mda | 200 | https://assets.publishing.service.gov.uk/media/6ab3f7c8a9c3d267bcccedd6/TS_41.2026_UK_USA_Amendment_Agreement_Cooperation_Atomic_Energy_Mutual_Defense_Purposes.pdf |
| usuk_tpd | 200 | https://www.whitehouse.gov/presidential-actions/2025/09/memorandum-of-understanding-between-the-government-of-the-united-states-of-america-and-the-government-of-the-united-kingdom-of-great-britain-and-northern-ireland-regarding-the-technology-prosperity-deal/ |
| useu_trade | 200 | https://www.govinfo.gov/content/pkg/DCPD-202500861/html/DCPD-202500861.htm |
| useu_trade | 200 | https://policy.trade.ec.europa.eu/news/joint-statement-united-states-european-union-framework-agreement-reciprocal-fair-and-balanced-trade-2025-08-21_en |
| useu_ttc | 200 | https://futurium.ec.europa.eu/en/node/5315 |
| useu_dpf | 200 | https://curia.europa.eu/site/upload/docs/application/pdf/2025-09/cp250106en.pdf |
| usin_defense | 200 | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2184622&reg=3&lang=2 |
| usin_trade | 200 | https://www.whitehouse.gov/briefings-statements/2026/02/united-states-india-joint-statement/ |
| usjp_summits | 200 | https://japan.kantei.go.jp/104/diplomatic/202510/28usa.html |
| usjp_summits | 200 | https://japan.kantei.go.jp/105/diplomatic/202603/20usa.html |
| usjp_summits | 200 | https://www.whitehouse.gov/fact-sheets/2026/03/fact-sheet-president-donald-j-trump-strengthens-u-s-japan-alliance-for-the-benefit-of-all-americans/ |
| usjp_trade | 200 | https://www.whitehouse.gov/fact-sheets/2025/09/fact-sheet-president-donald-j-trump-implements-a-historic-u-s-japan-framework-agreement/ |
| usjp_minerals | 200 | https://www.whitehouse.gov/briefings-statements/2025/10/united-states-japan-framework-for-securing-the-supply-of-critical-minerals-and-rare-earths-through-mining-and-processing/ |
| ukeu_summit | 200 | https://www.gov.uk/government/publications/ukeu-summit-key-documentation |
| ukeu_summit | 200 | https://www.gov.uk/government/speeches/pm-statement-to-the-house-of-commons-12-october-2026 |
| ukeu_summit | 200 | https://ec.europa.eu/commission/presscorner/detail/en/statement_26_955 |
| ukeu_tca | 200 | https://www.gov.uk/government/news/joint-statement-on-the-withdrawal-agreement-joint-committee-and-trade-and-cooperation-agreement-partnership-council-meetings-2-february-2026 |
| ukru_diplomatic | 200 | https://www.gov.uk/government/news/statement-foreign-office-summons-russian-ambassador-2-february-2026 |
| ukru_diplomatic | 200 | https://www.gov.uk/government/news/statement-foreign-office-summons-russian-ambassador-29th-april-2026 |
| ukru_incsea | 200 | https://www.gov.uk/government/publications/ukrussian-federation-protocol-of-amendments-to-agreement-concerning-prevention-of-incidents-at-sea-beyond-the-territorial-sea-15-july-1986-cs-russi |
| ukru_sanctions | 200 | https://www.gov.uk/government/publications/list-of-russia-sanctions-designations-16-june-2026 |
| ukru_sanctions | 200 | https://www.gov.uk/government/publications/the-uk-sanctions-list |
| ukin_ceta | 200 | https://www.gov.uk/government/news/historic-uk-india-free-trade-agreement-is-now-in-effect |
| ukin_ceta | 200 | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2274280&lang=2&reg=48 |
| ukin_tsi | 200 | https://www.gov.uk/government/publications/uk-india-technology-security-initiative-factsheet/uk-india-technology-security-initiative-factsheet |
| ukin_tsi | 200 | https://www.gov.uk/government/news/india-uk-joint-statement-9-october-2025 |
| ukcn_leaders | 200 | https://www.gov.uk/government/news/pm-meeting-with-president-xi-jinping-of-china-29-january-2026 |
| ukcn_leaders | 200 | https://www.fmprc.gov.cn/eng/xw/zyxw/202601/t20260129_11847645.html |
| ukcn_efd | 200 | https://www.gov.uk/government/publications/2025-uk-china-economic-and-financial-dialogue-policy-outcomes |
| ukcn_efd | 200 | https://www.gov.uk/government/publications/joint-readout-of-the-first-uk-china-financial-working-group/first-uk-china-financial-working-group-joint-readout |
| ukjp_raa | 200 | https://assets.publishing.service.gov.uk/media/654a5dede70413000ffc4986/TS_38.2023_UK_Japan_Agreement_Facilitation_Reciprocal_Access_Self_Defense_Forces_and_Armed_Forces.pdf |
| ukjp_gcap | 200 | https://assets.publishing.service.gov.uk/media/6762c109e6ff7c8a1fde9ab4/TS_98.2024_Convention_Establishment_GCAP_International_Government_Organisation.pdf |
| euru_relations | 200 | https://www.eeas.europa.eu/russia/european-union-and-russian-federation_en |
| euru_visa | 200 | https://home-affairs.ec.europa.eu/policies/international-affairs/engagement-partner-countries/russia_en |
| euru_sanctions | 200 | https://finance.ec.europa.eu/news/eu-adopts-21st-package-sanctions-against-russia-2026-07-23_en |
| euru_sanctions | 200 | https://finance.ec.europa.eu/eu-and-world/sanctions-restrictive-measures/sanctions-adopted-following-russias-military-aggression-against-ukraine_en |
| euin_fta | 200 | https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/india/eu-india-agreements_en |
| euin_fta | 200 | https://commission.europa.eu/topics/trade/eu-india-trade-agreement_en |
| euin_ttc | 200 | https://digital-strategy.ec.europa.eu/en/library/joint-statement-third-meeting-eu-india-trade-and-technology-council |
| eucn_summit | 200 | https://www.eeas.europa.eu/delegations/china/25th-eu-china-summit-eu-press-release_en |
| eucn_tic | 200 | https://ec.europa.eu/commission/presscorner/detail/en/statement_26_2122 |
| eucn_tic | 200 | https://www.mofcom.gov.cn/syxwfb/art/2026/art_663946a91806452182d02b3f0f62d4fc.html |
| eucn_hsd | 200 | https://www.mfa.gov.cn/wjdt_674879/gjldrhd_674881/202507/t20250703_11664024.shtml |
| eujp_summit | 200 | https://japan.kantei.go.jp/103/diplomatic/202507/23eu.html |
| eujp_summit | 200 | https://ec.europa.eu/commission/presscorner/detail/en/ac_25_1908 |
| eujp_sdp | 200 | https://www.eeas.europa.eu/sites/default/files/documents/2024/EU-Japan%20Security%20and%20Defence%20Partnership.pdf |
| eujp_sdp | 200 | https://www.eeas.europa.eu/sites/default/files/2025/documents/250723_EU-Japan-2025-07_FINAL_0.pdf |
| ruin_summit | 200 | http://en.kremlin.ru/supplement/6426 |
| ruin_relos | 200 | http://en.kremlin.ru/acts/news/78748 |
| ruin_relos | 200 | http://publication.pravo.gov.ru/document/0001202512150025 |
| rujp_peace | 200 | https://japan.kantei.go.jp/101_kishida/statement/202203/_00028.html |
| rujp_fisheries | 200 | https://www.jfa.maff.go.jp/j/press/kokusai/260320.html |
| rujp_fisheries | 200 | https://www.jfa.maff.go.jp/j/press/kokusai/251225.html |
| rujp_fisheries | 200 | https://www.jfa.maff.go.jp/j/press/kokusai/260619.html |
| incn_sr | 200 | https://www.fmprc.gov.cn/eng/gjhdq_665435/2675_665437/2711_663426/2713_663430/202508/t20250820_11692969.html |
| incn_sr | 200 | https://www.fmprc.gov.cn/eng/wjbzhd/202608/t20260826_12010652.html |
| incn_wmcc | 200 | https://www.mfa.gov.cn/eng/xw/wjbxw/202608/t20260807_12000162.html |
| incn_leaders | 200 | https://www.pmindia.gov.in/en/news_updates/pms-bilateral-meeting-with-chinese-president-xi-jinping/ |
| incn_leaders | 200 | https://www.fmprc.gov.cn/eng/xw/zyxw/202609/t20260913_12021206.html |
| incn_leaders | 200 | https://www.fmprc.gov.cn/eng/xw/fyrbt/202510/t20251024_11740246.html |
| injp_summit | 200 | https://www.pmindia.gov.in/en/news_updates/15th-india-japan-annual-summit-joint-statement-partnership-for-security-and-prosperity-of-our-next-generation/ |
| injp_summit | 200 | https://www.pmindia.gov.in/en/news_updates/16th-india-japan-annual-summit-joint-statement/ |
| injp_defence | 200 | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2301459&reg=48&lang=2 |
| injp_defence | 200 | https://www.pmindia.gov.in/en/news_updates/joint-declaration-on-security-cooperation-between-india-and-japan/ |
| cnjp_mamc | 200 | https://www.mod.go.jp/j/approach/exchange/area/2023/pdf/20230331_chn-j.pdf |
| cnjp_mamc | 200 | https://www.mod.go.jp/j/approach/exchange/area/2023/pdf/20230516_chn-j.pdf |
| cnjp_maritime | 200 | https://www.mod.go.jp/j/press/wp/wp2026/backdata/siryo53.csv |
| cnjp_leaders | 200 | https://www.mfa.gov.cn/eng/xw/zyxw/202511/t20251101_11745380.html |
| cnjp_leaders | 200 | https://www.mfa.gov.cn/eng/xw/fyrbt/202605/t20260507_11906405.html |
| cnjp_seafood | 200 | https://www.fmprc.gov.cn/mfa_eng/xw/fyrbt/202511/t20251119_11756196.html |
| all_unsc | 200 | https://research.un.org/en/docs/sc/quick/veto |
| all_unsc | 200 | https://main.un.org/securitycouncil/en/content/current-members |
| all_p5 | 200 | https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/2022/01/03/p5-statement-on-preventing-nuclear-war-and-avoiding-arms-races/ |
| all_p5 | 200 | https://www.mfa.gov.cn/web/zyxw/202201/t20220103_10478507.shtml |
| all_ctbt | 403 | https://www.ctbto.org/our-mission/states-signatories |
| all_ctbt | 200 | https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVI-4&chapter=26&clang=_en |
| all_iaea | 403 | https://www.iaea.org/about/governance/board-of-governors |
| all_iter | 200 | https://www.iter.org/about/iter-members |
| all_ats | 200 | https://www.ats.aq/devAS/Parties?lang=e |
| all_npfc | 200 | https://www.npfc.int/ |
| all_wmo | 200 | https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/operational-information-service-ois/rths-country |
| all_wmo | 200 | https://wmo.int/media/news/wmo-overhauls-data-exchange-policy |
| all_cospas | 200 | https://www.cospas-sarsat.int/en/about-us/participants |
| all_nptrevcon | 200 | https://www.un.org/en/conferences/treaty-on-the-non-proliferation-of-nuclear-weapons-npt-2026 |
| all_nptrevcon | 200 | https://www.state.gov/releases/office-of-the-spokesperson/2026/05/conclusion-of-the-2026-nuclear-non-proliferation-treaty-review-conference/ |
| all_nptrevcon | 200 | https://www.fmprc.gov.cn/eng/xw/fyrbt/202605/t20260525_11917325.html |
| all_nptrevcon | 202 | https://digitallibrary.un.org/record/4082389/files/NPT_CONF.2026_PC.III_DEC.1-ZH.pdf |
| kremlin | ERR URLError | https://kremlin.ru |
| fmprc | 200 | https://www.fmprc.gov.cn |
| mid | 200 | https://mid.ru |
| stategov | 200 | https://www.state.gov |
| undl | 202 | https://digitallibrary.un.org |
| untreaty | 200 | https://treaties.un.org |
| cntreaty | 200 | http://treaty.mfa.gov.cn |
| pravo | 200 | http://publication.pravo.gov.ru |
| fedreg | 200 | https://www.federalregister.gov |
| crs | 403 | https://crsreports.congress.gov |
| uscc | 200 | https://www.uscc.gov |
| gacs | 412 | http://stats.customs.gov.cn |
| census | 200 | https://www.census.gov/foreign-trade/balance/c5700.html |
| comtrade | 200 | https://comtradeplus.un.org |
| imfdata | 403 | https://data.imf.org |
| portwatch | 200 | https://portwatch.imf.org |
| gats | 200 | https://apps.fas.usda.gov/gats |
| crea | 200 | https://energyandcleanair.org |
| cbr | 200 | https://www.cbr.ru/eng/statistics |
| safe | 200 | https://www.safe.gov.cn |
| tic | 200 | https://home.treasury.gov/data/treasury-international-capital-tic-system |
| swift | 403 | https://www.swift.com |
| bisorg | 200 | https://data.bis.org |
| wto | 200 | https://www.wto.org |
| ustr | 200 | https://ustr.gov |
| mofcom | 200 | http://www.mofcom.gov.cn |
| usgs | 200 | https://www.usgs.gov/centers/national-minerals-information-center |
| eiau | 200 | https://www.eia.gov/uranium/marketing/ |
| rosstat | ERR URLError | https://rosstat.gov.ru |
| ofac | 200 | https://ofac.treasury.gov |
| bis | 200 | https://www.bis.gov |
| eumap | 200 | https://www.sanctionsmap.eu |
| doj | 200 | https://www.justice.gov |
| courtl | ERR URLError | https://www.courtlistener.org |
| cac | 200 | https://www.cac.gov.cn |
| caisi | 200 | https://www.nist.gov/caisi |
| ccw | 202 | https://meetings.unoda.org |
| unai | 200 | https://www.un.org/digital-emerging-technologies/ |
| poldecl | 200 | https://www.state.gov |
| openalex | 200 | https://openalex.org |
| eto | 200 | https://eto.tech |
| epoch | 200 | https://epoch.ai |
| aiindex | 200 | https://hai.stanford.edu/ai-index |
| wipo | 200 | https://patentscope.wipo.int |
| track2 | 200 | https://www.brookings.edu |
| ctbto | 403 | https://www.ctbto.org |
| iris | 200 | https://ds.iris.edu |
| pris | 200 | https://pris.iaea.org |
| iaea | 403 | https://www.iaea.org |
| compliance | 200 | https://www.state.gov |
| newstart | 200 | https://www.state.gov |
| npt | 200 | https://www.un.org/en/conferences/npt2026 |
| launchnotif | 200 | https://www.state.gov |
| nnotebook | 403 | https://thebulletin.org |
| sipriyb | 200 | https://www.sipri.org |
| japanjs | 403 | https://www.mod.go.jp/js/press/index.html |
| taiwanmnd | 200 | https://www.mnd.gov.tw |
| rokjcs | 200 | https://www.jcs.mil.kr |
| norad | 403 | https://www.norad.mil |
| uscg | 403 | https://www.news.uscg.mil |
| dod | 403 | https://www.defense.gov |
| cnmod | 200 | http://eng.mod.gov.cn |
| rumod | ERR URLError | https://eng.mil.ru |
| spacetrack | 200 | https://www.space-track.org |
| celestrak | 200 | https://celestrak.org |
| mcdowell | 200 | https://planet4589.org |
| unoosa | 200 | https://www.unoosa.org/oosa/en/spaceobjectregister/index.html |
| sipri | 200 | https://www.sipri.org/databases |
| unroca | 202 | https://www.unroca.org |
| acled | 200 | https://acleddata.com |
| firms | 200 | https://firms.modaps.eosdis.nasa.gov |
| car | 200 | https://www.conflictarm.com |
| adsb | 200 | https://globe.adsbexchange.com |
| copernicus | 200 | https://dataspace.copernicus.eu |
| landsat | 200 | https://earthexplorer.usgs.gov |
| worldview | 200 | https://worldview.earthdata.nasa.gov |
| gfw | 200 | https://globalfishingwatch.org |
| iss | 200 | https://www.nasa.gov/international-space-station/ |
| iter | 200 | https://www.iter.org |
| ats | 200 | https://www.ats.aq |
| npfc | 200 | https://www.npfc.int |
| wmo | 200 | https://wmo.int |
| cospas | 200 | https://www.cospas-sarsat.int |
| natureidx | 200 | https://www.nature.com/nature-index |
| opendoors | 200 | https://opendoorsdata.org |
| pew | 200 | https://www.pewresearch.org |
| levada | 200 | https://www.levada.ru/en/ |
| ciss | 200 | https://ciss.tsinghua.edu.cn |
| ccga | 200 | https://globalaffairs.org |
| xinhua | 200 | https://www.news.cn |
| tass | 200 | https://tass.com |
| fcdo | 200 | https://www.gov.uk/government/organisations/foreign-commonwealth-development-office |
| uktreaty | 200 | https://www.gov.uk/government/collections/bilateral-and-multilateral-treaties-published-in-the-treaty-series-2018 |
| ons | 200 | https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments |
| boe | 200 | https://www.bankofengland.co.uk/boeapps/database |
| hansard | 403 | https://hansard.parliament.uk |
| uksanctions | 200 | https://www.gov.uk/government/publications/the-uk-sanctions-list |
| eeas | 200 | https://www.eeas.europa.eu/eeas/press-material_en |
| ecpress | 200 | https://ec.europa.eu/commission/presscorner/home/en |
| eurlex | 202 | https://eur-lex.europa.eu |
| eurostat | 200 | https://ec.europa.eu/eurostat/web/international-trade-in-goods |
| ecbdata | 200 | https://data.ecb.europa.eu |
| epoeil | 200 | https://oeil.secure.europarl.europa.eu |
| mea | 403 | https://www.mea.gov.in |
| pib | 200 | https://pib.gov.in |
| tradestat | 200 | https://tradestat.commerce.gov.in |
| rbi | 200 | https://www.rbi.org.in/Scripts/Statistics.aspx |
| isro | 200 | https://www.isro.gov.in |
| sansad | 200 | https://sansad.in/ls |
| mofaj | 403 | https://www.mofa.go.jp |
| kantei | 200 | https://japan.kantei.go.jp |
| jpcustoms | 200 | https://www.customs.go.jp/toukei/info/index_e.htm |
| boj | 200 | https://www.stat-search.boj.or.jp/index_en.html |
| jaxa | 200 | https://global.jaxa.jp |
| kokkai | 200 | https://kokkai.ndl.go.jp |
| jfa | 200 | https://www.jfa.maff.go.jp/j/press/index.html |

### Checker script (not committed separately; stdlib only)

Run it as `python3 check_urls.py <repo-root>`.

```python
#!/usr/bin/env python3
"""Validate channels.json / sources.json and check every URL (stdlib only).

usage: python3 check_urls.py <repo-root>
Prints a markdown table: id | status | url. Status is the final HTTP code,
or ERR <reason>. Uses a browser-like User-Agent and one retry on errors.
"""
import json, ssl, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(sys.argv[1])
POWERS = {"US", "UK", "EU", "RU", "IN", "CN", "JP"}
STATUSES = {"active", "limited", "dormant", "ended", "contested"}
EV = set("ABCDEF")
TOPICS = {"diplo", "trade", "ai", "nuclear", "military", "coop", "sentiment"}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CTX = ssl.create_default_context()

ch = json.loads((ROOT / "data/curated/channels.json").read_text())
src = json.loads((ROOT / "data/curated/sources.json").read_text())

# ---- schema checks ----
errs = []
for k, v in ch.items():
    for f in ("title", "dyad", "status", "desc", "links", "asof"):
        if f not in v:
            errs.append(f"channel {k}: missing {f}")
    if v["status"] not in STATUSES:
        errs.append(f"channel {k}: status {v['status']}")
    d = v["dyad"]
    if d != "All three" and not (len(d.split("–")) == 2 and set(d.split("–")) <= POWERS):
        errs.append(f"channel {k}: dyad {d}")
    for m in v.get("members", []):
        if m not in POWERS:
            errs.append(f"channel {k}: member {m}")
    for l in v["links"]:
        if not l.get("url", "").startswith("http") or not l.get("label"):
            errs.append(f"channel {k}: bad link {l}")
ids = [s["id"] for s in src]
if len(ids) != len(set(ids)):
    errs.append("duplicate source ids")
for s in src:
    if set(s) != {"id", "name", "url", "pub", "ev", "topics", "cov", "cad", "watch", "cav"}:
        errs.append(f"source {s['id']}: keys {sorted(s)}")
    if s["ev"] not in EV or not set(s["topics"]) <= TOPICS or not s["cov"] or not set(s["cov"]) <= POWERS:
        errs.append(f"source {s['id']}: ev/topics/cov")
print(f"channels={len(ch)} sources={len(src)} schema_errors={len(errs)}")
for e in errs:
    print("  ", e)

# ---- URL checks ----
targets = [(k, l["url"]) for k, v in ch.items() for l in v["links"]] + [(s["id"], s["url"]) for s in src]


def fetch(u):
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "text/html,application/pdf,*/*"})
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                r.read(2048)
                return str(r.status)
        except urllib.error.HTTPError as e:
            return str(e.code)
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                return "ERR " + type(e).__name__
            time.sleep(2)


with ThreadPoolExecutor(10) as ex:
    res = list(ex.map(lambda t: (t[0], fetch(t[1]), t[1]), targets))
print("\n| id | status | url |\n|---|---|---|")
for k, st, u in res:
    print(f"| {k} | {st} | {u} |")
from collections import Counter
print("\nstatus counts:", dict(Counter(st for _, st, _ in res)))
```
