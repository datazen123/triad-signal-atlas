# API endpoint verification

Checked 2026-10-12 via WebFetch, after the permissions were approved.

**Caveat about the samples:** WebFetch passes pages through a summarizer that will not quote more than
about 125 characters verbatim. So the samples below are exact short quotes where marked `verbatim`. Everything
else is a structured dump that the fetch tool reported field by field (key names and values as returned), not a
raw byte-for-byte copy.

Status legend:
- **VERIFIED**: live call succeeded
- **DOCS-ONLY**: live call failed; structure confirmed from official docs/spec
- **FAILED**: neither worked

| # | Endpoint | Status |
|---|----------|--------|
| 1 | OpenAlex | DOCS-ONLY. Every live call to api.openalex.org returned CLIENT_ERROR (6 attempts, several URL forms) |
| 2 | Nobel v2.1 | DOCS-ONLY. api.nobelprize.org returned CLIENT_ERROR every time; the OpenAPI spec was read from SwaggerHub |
| 3 | Federal Register documents + yearly facets | VERIFIED |
| 4 | UN Comtrade preview | VERIFIED for 156→643. 643 as reporter returns `count:0`. 842 was inconclusive |
| 5 | Wayback availability | VERIFIED |
| 6 | OFAC SDN/ADD CSVs | FAILED. All 4 URLs and the docs pages returned CLIENT_ERROR |
| 7 | CelesTrak SATCAT | csv: FAILED (ROBOTS_DISALLOWED for WebFetch only). Columns and codes are DOCS-VERIFIED |
| 8 | IMF PortWatch | VERIFIED. FeatureServer URL found and queried |
| 9 | World Bank | VERIFIED |
| 10 | UN DESA Migrant Stock 2024 | Download URLs VERIFIED. xlsx unreadable via WebFetch (binary). **No bilateral figures obtained** |

CLIENT_ERROR here is a fetch-tool failure. It does not mean the API is down: Comtrade failed intermittently, then
succeeded on a repeat. A plain urllib call from GitHub Actions will very likely work. Test with a smoke run.

---

## 1. OpenAlex — DOCS-ONLY

URLs tried (all CLIENT_ERROR):
- `/works?filter=authorships.institutions.country_code:US,authorships.institutions.country_code:CN&group_by=publication_year` (with and without mailto)
- the lowercase `us`/`cn` + `publication_year:2024` + `per_page=1` variant
- the trivial `/works?filter=publication_year:2024&per_page=1`

From docs.openalex.org (filter-entity-lists and get-groups-of-entities pages):
- **Repeating a key with commas = AND.** The docs example `institutions.country_code:fr,institutions.country_code:gb` returns
  "works with an author from France and an author from the UK". `fr+gb` is equivalent. A pipe `fr|gb` = OR (max 100 values).
- **Filters are case-insensitive** (verbatim: "Filters are case-insensitive"). So `us`/`cn` are equivalent to `US`/`CN`.
- **mailto / api_key:** not mentioned on these pages. `mailto=` has historically been accepted (polite pool). This is unconfirmed here;
  sending it is harmless.
- Response shape:
  - `meta.count` (int: total matching works). `meta.db_response_time_ms`, `meta.page`, `meta.per_page`, `meta.groups_count`
    (number of groups on this page; null if none).
  - `group_by[]`: `{ "key": <raw value, string>, "key_display_name": <string>, "count": <int> }`
  - `results` is a list (empty when you use group_by).
  - At most 200 groups per response. Paged group results are sorted by key.
- A per-year total is `filter=...,publication_year:2024&per_page=1`, then read `meta.count`. NOT live-tested.
- Collector tip: `int(g["key"])` for the year, `g["count"]`.

## 2. Nobel Prize API v2.1 — DOCS-ONLY

Live `api.nobelprize.org/2.1/laureates?limit=…` and `/2.1/laureate/1` gave CLIENT_ERROR every time.
Schema source: `https://api.swaggerhub.com/apis/NobelMedia/NobelMasterData/2.1` (official OpenAPI spec).
- Top level: `laureates[]`, `meta`, `links`.
- Birth (persons): `laureates[].birth.place.{city, country, cityNow, countryNow, continent, locationString}`
  - `country` = translation `{en, se, no}`. This is the name at the time of birth.
  - `countryNow` = translationWithSameas `{en, se, no, sameAs: [url, ...]}`. This is the current country name.
  - **There is no ISO code field.** The only identifiers are the `sameAs` URLs (Wikipedia/Wikidata). Map `countryNow.en` → ISO yourself.
  - Organizations have no `birth`. The spec has `founded.place` (same location schema).
- Per prize: `laureates[].nobelPrizes[].affiliations[].{name, nameNow, nativeName, city, country, cityNow, countryNow, locationString}`.
  `countryNow.en` is the current country name.
  - (The prize year is `nobelPrizes[].awardYear` and the category is `nobelPrizes[].category.en`. These come from prior knowledge,
    not re-confirmed in this spec read.)
- Pagination: `meta.{offset, limit, count, ...filters}`, `links.{first, prev, self, next, last}`.
  `limit` has minimum 1 and **no documented maximum or default**. Loop on `links.next` until absent, or use `offset += limit` until
  `offset >= meta.count`. A large limit (e.g. 1000) is commonly used. Unverified.

## 3. Federal Register — VERIFIED

`documents.json?per_page=1&conditions[term]="entity list"&conditions[agencies][]=industry-and-security-bureau`
- Top-level keys: `count` (int), `description` (str), `total_pages` (int), `next_page_url` (str), `results` (array)
- **`count` = 355** (2026-10-12)
- `results[0]` keys: `title, type, abstract, document_number, html_url, pdf_url, public_inspection_pdf_url, publication_date, agencies, excerpts`
- Latest result: "Revisions to the Entity List" / "Removal From the Entity List", publication_date 2026-08-24

`documents/facets/yearly?...same conditions`
- A dict keyed by a **full date string `YYYY-01-01`** (not a bare year), covering 1994–2026. Each value is `{"count": int, "name": "YYYY"}`.
- verbatim:
  ```
  "2026-01-01":{"count":5,"name":"2026"}
  "2025-01-01":{"count":16,"name":"2025"}
  "2024-01-01":{"count":34,"name":"2024"}
  ```
- Collector: `{v["name"]: v["count"] for v in resp.values()}`

## 4. UN Comtrade public preview — VERIFIED (156)

`/public/v1/preview/C/A/HS?reporterCode=156&period=2023&partnerCode=643&cmdCode=TOTAL&flowCode=X`
- Top-level keys: `elapsedTime` ("1.05 secs"), `count` (1), `data` (array), `error` ("")
- `data[0]` (all fields): `typeCode:"C", freqCode:"A", refPeriodId:20230101, refYear:2023, refMonth:52, period:"2023",
  reporterCode:156, reporterISO:null, reporterDesc:null, flowCode:"X", flowDesc:null, partnerCode:643, partnerISO:null,
  partnerDesc:null, partner2Code:0, ..., classificationCode:"H6", cmdCode:"TOTAL", cmdDesc:null, customsCode:"C00", mosCode:"0",
  motCode:0, qty:0.0, netWgt:0.0, grossWgt:0.0, cifvalue:null, fobvalue:110935409106.0, primaryValue:110935409106.0,
  legacyEstimationFlag:4, isReported:false, isAggregate:true`
- **Value field: `data[i].primaryValue`** (USD, float). China→Russia exports 2023 = 110,935,409,106. Repeated twice with the same result.
- The preview returns **null `*Desc`/`*ISO` fields**, so map codes yourself (156 CHN, 643 RUS, 842 USA).
- `reporterCode=643` (period 2023, flowCode X, all partners): **`count: 0`, empty `data`.** Russia does not report, so use mirror flows.
- `reporterCode=842`: flowCode M with partner 156 → CLIENT_ERROR twice. flowCode X → the tool got "unreadable binary" data. **Inconclusive.**
  The US does report to Comtrade, so expect it to work. Possibly rate limiting: space the calls out (sleep 2–5 s), and retry on 429/5xx.
- The endpoint is flaky under rapid or parallel requests. Do requests sequentially with retries.

## 5. Wayback availability — VERIFIED

verbatim:
```json
{"url": "iter.org", "archived_snapshots": {"closest": {"status": "200", "available": true, "url": "http://web.archive.org/web/20261010220044/https://www.iter.org/", "timestamp": "20261010220044"}}}
```
Paths: `archived_snapshots.closest.{status (str), available (bool), url (str), timestamp (str YYYYMMDDhhmmss)}`.
Guard for `archived_snapshots == {}`.

## 6. OFAC SDN — FAILED (no live or docs confirmation)

Results:
- `https://www.treasury.gov/ofac/downloads/sdn.csv`: CLIENT_ERROR
- `https://www.treasury.gov/ofac/downloads/add.csv`: CLIENT_ERROR
- `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV`: CLIENT_ERROR (×2)
- `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/ADD.CSV`: CLIENT_ERROR (×2)
- `https://www.treasury.gov/ofac/downloads/dat_spec.txt`: CLIENT_ERROR
- `ofac.treasury.gov/specially-designated-nationals-list-data-formats-data-schemas` → 302 to `https://sanctionslist.ofac.treas.gov/Home/SdnList`
  (a JS app). Its `/static/` page → CLIENT_ERROR.

Unverified prior knowledge (test in CI):
- Prefer the sanctionslistservice URLs. The treasury.gov/ofac/downloads paths are legacy and may redirect.
- SDN.CSV has **no header row**, 12 columns: `ent_num, SDN_Name, SDN_Type, Program, Title, Call_Sign, Vess_type, Tonnage, GRT, Vess_flag, Vess_owner, Remarks`.
  - Program is index 3. Multiple programs appear as `RUSSIA-EO14024] [IRAN` style; split on `] [`.
  - **No country column.** Some country info is in Remarks.
- ADD.CSV has no header, 6 columns: `ent_num, Add_num, Address, City/State/Province/Postal Code, Country, Add_remarks`. Country is index 4.
  Join to SDN on `ent_num`.
- The null marker is `-0-` (often padded with a trailing space). The file may end with a `\x1a` EOF line. Use `csv.reader`, strip fields,
  and skip rows with fewer than 2 columns.

## 7. CelesTrak SATCAT — csv FAILED (robots); schema DOCS-VERIFIED

`https://celestrak.org/pub/satcat.csv` returned `ROBOTS_DISALLOWED`. This is WebFetch honoring robots.txt, and it is not an
indication that urllib will fail. Set a descriptive User-Agent, and download at most once per day (CelesTrak rate-limits repeat downloads).

From `celestrak.org/satcat/satcat-format.php`, the CSV columns in order:
`OBJECT_NAME, OBJECT_ID, NORAD_CAT_ID, OBJECT_TYPE, OPS_STATUS_CODE, OWNER, LAUNCH_DATE, LAUNCH_SITE, DECAY_DATE, PERIOD, INCLINATION, APOGEE, PERIGEE, RCS, DATA_STATUS_CODE, ORBIT_CENTER, ORBIT_TYPE`
(the header row presence is not live-confirmed, but the named columns imply a header; use `csv.DictReader`).
- OBJECT_TYPE: `PAY`, `R/B`, `DEB`, `UNK`
- OPS_STATUS_CODE (`satcat/status.php`): `+` operational, `-` nonoperational, `P` partially operational, `B` backup/standby,
  `S` spare, `X` extended mission, `D` decayed, `?` unknown. **Active = `+ P B S X`.**
- OWNER codes (`satcat/sources.php`): US=`US`, China=`PRC`, Russia/USSR=`CIS` ("Commonwealth of Independent States (former USSR)";
  no separate Russia code), ESA=`ESA`, India=`IND`, Japan=`JPN`, UK=`UK`.

## 8. IMF PortWatch — VERIFIED

Found via the Hub search API `https://portwatch.imf.org/api/search/v1/collections/all/items?q=chokepoint`:
- Daily_Chokepoints_Data (item 3da2b9ca97684916b75c4013f95d18ab):
  `https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer`
- Chokepoints (static metadata): `.../PortWatch_chokepoints_database/FeatureServer`
- Disruptions: `.../portwatch_disruptions_database/FeatureServer`

Verified query:
`https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query?where=1%3D1&outFields=*&resultRecordCount=2&orderByFields=date%20DESC&f=json`
- Top-level: `objectIdFieldName, uniqueIdField, globalIdFieldName, fields, exceededTransferLimit (true), features[]`
- Fields: `date` (esriFieldTypeDateOnly), `year, month, day` (int), `portid, portname` (str), `n_container, n_dry_bulk,
  n_general_cargo, n_roro, n_tanker, n_cargo, n_total` (int), `capacity_container, capacity_dry_bulk, capacity_general_cargo,
  capacity_roro, capacity_tanker, capacity_cargo, capacity` (int), `ObjectId` (OID)
- `features[0].attributes`:
  `{date:"2026-09-06", year:2026, month:9, day:6, portid:"chokepoint1", portname:"Suez Canal", n_container:9, n_dry_bulk:2,
  n_general_cargo:1, n_roro:2, n_tanker:16, n_cargo:14, n_total:30, capacity_container:326827, ..., capacity:1081066, ObjectId:2407}`
- **`date` is a `"YYYY-MM-DD"` string** (DateOnly), not epoch ms. The latest data was 2026-09-06, about a 5-week lag.
- To filter one chokepoint, use `where=portid%3D%27chokepoint1%27`. Paginate with `resultOffset` while `exceededTransferLimit` is true.

## 9. World Bank — VERIFIED

`/v2/country/CHN;RUS;USA/indicator/NE.TRD.GNFS.ZS?format=json&date=2020:2024`
- A 2-element array. `[0]` = `{page:1, pages:1, per_page:50, total:15, sourceid:"2", lastupdated:"2026-10-08"}`
- `[1]` = 15 rows. Row: `{indicator:{id,value}, country:{id:"CN", value:"China"}, countryiso3code:"CHN", date:"2024", value:37.956…, unit:"", obs_status:"", decimal:0}`
- verbatim (truncated): `{"indicator":{"id":"NE.TRD.GNFS.ZS","value":"Trade (% of GDP)"},"country":{"id":"CN","value":"China"},`
- `value` can be null for years that are not yet available. `date` is a string. Add `per_page=1000`.

## 10. UN DESA International Migrant Stock 2024 — partial

Official page (VERIFIED): https://www.un.org/development/desa/pd/content/international-migrant-stock
2024 downloads:
- Destination and origin (bilateral):
  https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx
- By destination: .../files/undesa_pd_2024_ims_stock_by_sex_and_destination.xlsx
- By origin: .../files/undesa_pd_2024_ims_stock_by_sex_and_origin.xlsx

The bilateral xlsx came back as `[binary data]`, so WebFetch cannot parse it. **None of the 12 requested pair figures were obtained.**
I did not substitute numbers from memory. Options:
(a) In the Action, download the xlsx, unzip it with `zipfile`, and parse `xl/sharedStrings.xml` + `xl/worksheets/sheet*.xml` with
    `xml.etree` (stdlib only). Table 1 holds destination rows × origin columns, by year.
(b) Extract the 12 values by hand once into a committed CSV. The data is updated only every few years.
