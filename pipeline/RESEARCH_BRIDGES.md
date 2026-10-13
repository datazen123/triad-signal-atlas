# Research log: bridge stories (`data/curated/bridges.json`)

Started 2026-10-13. The log records the method, queries, dead ends and URL checks.

## Method

- Starting point: Ilan Kelman's China/Taiwan case study at https://www.disasterdiplomacy.org/chinataiwan.html. Its BBC references (1999 aid offer, 2002 Matsu water, 2002 fishermen rescue) were fetched. All of them resolve under `news.bbc.co.uk/2/hi/...`.
- Source order: official primary pages (TAO/gwytb.gov.cn, ARATS, SEF, Taiwan Presidential Office, MAC), then peer-reviewed work, then reputable press.
- Quotes are translated from text that appears verbatim on the cited page. The original Chinese is kept in `note`.
- `conf` rules: `ok` = a primary or scholarly page that was fetched confirms the core claim; `check` = press only, or a primary page that blocks automated fetching; `unconfirmed` = kept with a note.

## Queries used (PRC–Taiwan)

- 九二一大地震 大陸 援助 紅十字會 婉拒 陸委會 1999
- 陆委会 新闻稿 汶川地震 红十字会 搜救队 2008 捐款; 四川 地震 台灣 捐款 搜救 救災 2008 (restricted to mac/sef/gwytb/taiwan.cn)
- 莫拉克 台风 救灾 活动板房 海协会 海基会; 陸委會 莫拉克 大陸 捐款 組合屋
- 金門協議 1990 紅十字會 遣返 全文; 辜汪會談 1993 新加坡 四項協議
- 汪道涵 "一个中国并不等于中华人民共和国"; 江泽民 八项主张 "中国人不打中国人"
- 钱其琛 2002 民进党; 习近平 "特殊历史遭遇"; 馬習會 2015 總統府
- 2024 花莲地震 国台办; 金門 自大陸引水 2018; 慈濟 1991 華東水災; 高秉涵 老兵 骨灰

## Dead ends (PRC–Taiwan)

- `covid-19.chinadaily.com.cn/...` (2008 Sichuan and 2009 Morakot reports, 2010 Kinmen–Xiamen joint search-and-rescue drill): every URL returns a soft-404 page, and the `www.chinadaily.com.cn` versions return 404. Not cited. The 2010 joint drill story was dropped for lack of a live source.
- `taiwantoday.tw` (2008 Red Cross team "first" claim): redirect loop to `vpn.html`. Not cited.
- `mac.gov.tw` news pages (2018 Hualien thanks, 2023 Gansu condolences, Sichuan donation account): HTTP 403 to both urllib and WebFetch. Not cited. Facts that depend only on them are flagged in `note`.
- `art.archives.gov.tw/Theme.aspx?MenuID=645` (1987 family-visit Red Cross registration): 301 to the archives homepage. Not cited.
- `thenewslens.com/article/201071` (DW figures on Taiwan's Sichuan donations): 403.
- `sanfrancisco.china-consulate.gov.cn` (Jiang's eight points): redirects to the consulate homepage.
- Wang Daohan's 1997 "one China jointly built" remark: no primary record was found, only later commentary. Kept as `unconfirmed`.
- Hu Jintao–Wu Poh-hsiung 2008 "建立互信、搁置争议、求同存异、共创双赢": no primary text was found in one search. Not added.
- Tzu Chi's "first foreign NGO registered in the PRC" (2008 vs 2010): sources conflict. Not added.

## Queries and sources (other pairs)

- Started from Kelman's Greece/Turkey and India/Pakistan case pages on disasterdiplomacy.org, then looked for official pages: mfa.am, PIB (India), World Bank, UN (Black Sea Initiative, OHCHR Ukraine mission), ICRC, NASA, State Department and White House archives, Japan Kantei, PRC MFA, ROK Ministry of Unification, OFAJ, CMP Cyprus, ENRS.
- Chinese-language queries were used for China–Japan: 日本国际救援队 汶川地震 外交部 发言人 感谢; 温家宝 2011年5月 福岛 灾民.
- Scholarly sources: Ker-Lindsay (2000) via LSE Research Online; Herington & Lee (2014) in Globalization and Health; the smallpox history article in PMC; the PA-X peace agreements database (University of Edinburgh).

## Dead ends (other pairs)

- `mofa.go.jp` (2008 JDR team dispatch; 2011 list of accepted assistance): HTTP 403 to urllib, curl and WebFetch. Cited only as secondary links marked "blocks automated fetching"; the core claims rest on PRC MFA pages.
- `olympics.com` (IOC decision on the unified Korean hockey team): timeouts and HTTP/2 stream errors. Not cited; Korea Herald and NPR used instead (`check`).
- `mea.gov.in` (23 Apr 2025 briefing on the Indus Waters Treaty): 403. Replaced by the PIB PDF compilation, which quotes the CCS decision.
- `mofa.gov.pk` (Kartarpur renewal, Indus statements): TLS handshake failure (EOF) from urllib. Not cited.
- `2017-2020.usaid.gov` (Danang dioxin fact sheet) and `congress.gov` CRS R44268: TLS failure and 403. The US Embassy Vietnam fact sheet was used instead.
- `defense.gov`, `dtra.mil`, `crisisgroup.org`, `mfa.gr`, `civilnet.am`: 403. Kept only as secondary links labelled "page blocks automated fetching"; no story relies on them alone for `ok`.
- `iwm.org.uk` (Christmas truce): 403/301. National Army Museum used instead.
- `iz.poznan.pl` PDF of the 1965 bishops' letter: 404. ENRS used instead.
- `federalregister.gov` (NSPM-5 on Cuba): redirects bots to `unblock.federalregister.gov`. The State Department 2017–2021 archive page was used instead.
- `www.gov.cn/ldhd/2011-05/21/content_1868565.htm` (Wen Jiabao in Fukushima): 404. The PRC Niigata consulate article covers the visit and the 2011 rescue team.
- `vn.usembassy.gov/pr201711010-...` (2017 Danang ceremony): 404.
- `disasterdiplomacy.org/kerlindsay2000.pdf`: a scanned PDF with no text layer. The LSE abstract was used for the claim.
- Not added for lack of a fetchable source: Kinmen–Xiamen joint maritime search-and-rescue drill (2010), Hu Jintao–Wu Poh-hsiung "建立互信、搁置争议" (2008), and Turkey's aid after the 1988 Spitak earthquake.

## Validation and URL check (2026-10-13)

- `python3 -m json.tool data/curated/bridges.json` passes.
- The checker script below confirms the schema keys and enums, and that all 49 ids are unique.
- URL check: 84 of 91 unique URLs returned 200. The 7 that returned 403 are bot-blocking official or press pages, each labelled as such in `src` and `note`.
- `english.president.gov.tw` redirects HEAD requests to its homepage but serves the article on GET. Both NEWS/4628 and NEWS/4779 were re-checked with GET and return the cited text.
- `news.tvbs.com.tw/english/2451354` redirects to `t.media/2451354`, which serves the same article.

| status | url |
|---|---|
| 200 | http://cpc.people.com.cn/GB/64107/65708/65722/4444435.html |
| 200 | http://news.bbc.co.uk/2/hi/asia-pacific/1969202.stm |
| 200 | http://news.bbc.co.uk/2/hi/asia-pacific/2117211.stm |
| 200 | http://news.bbc.co.uk/2/hi/asia-pacific/453309.stm |
| 200 | http://www.arats.com.cn/xieyi/201305/t20130514_4203529.htm |
| 200 | https://2009-2017.state.gov/t/isn/4785.htm |
| 200 | https://2017-2021.state.gov/cuba-sanctions/ |
| 200 | https://asianews.network/mainland-china-offers-aid-to-taiwan-after-powerful-earthquake/ |
| 200 | https://barenboim-said.org/ |
| 200 | https://documents.un.org/doc/undoc/gen/n25/175/44/pdf/n2517544.pdf |
| 200 | https://dpaa-mil.sites.crmforce.mil/dpaaProfile?id=a0Jt000000ffRF3EAM |
| 200 | https://english.president.gov.tw/NEWS/4628 -> https://english.president.gov.tw/ |
| 200 | https://english.president.gov.tw/NEWS/4779 -> https://english.president.gov.tw/ |
| 200 | https://enrs.eu/news/letter-of-reconciliation-of-the-polish-bishops-to-the-german-bishops |
| 200 | https://globalizationandhealth.biomedcentral.com/articles/10.1186/s12992-014-0071-y -> https://link.springer.com/article/10.1186/s12992-014-0071-y?error=cookies_not_supported&code=64439009-cb6f-4ab1-b140-d1240e19a6a4 |
| 200 | https://interpret.csis.org/translations/general-secretary-xi-jinping-meets-with-joint-delegation-of-taiwan-peaceful-reunification-groups/ |
| 200 | https://japan.kantei.go.jp/97_abe/statement/201612/1220678_11021.html |
| 200 | https://lib.taiwan.cn/2015wenxian/202101/t20210119_12319021.htm |
| 200 | https://lib.taiwan.cn/shetai/201109/t20110921_2075833.htm |
| 200 | https://m.koreaherald.com/article/1566985 |
| 200 | https://news.pts.org.tw/article/401132 |
| 200 | https://news.sina.com.cn/c/2002-01-24/455649.html |
| 200 | https://news.tvbs.com.tw/english/2451354 -> https://t.media/2451354 |
| 200 | https://newtalk.tw/news/view/2011-10-03/18332 |
| 200 | https://newyork.china-consulate.gov.cn/chn/fyrth/200805/t20080520_4262242.htm |
| 200 | https://niigata.china-consulate.gov.cn/xwdt/202103/t20210308_10030400.htm |
| 200 | https://obamawhitehouse.archives.gov/the-press-office/2014/12/17/statement-president-cuba-policy-changes |
| 200 | https://obamawhitehouse.archives.gov/the-press-office/2015/07/01/presidential-letter-re-establishing-diplomatic-relations-and-permanent |
| 200 | https://obamawhitehouse.archives.gov/the-press-office/2016/05/27/remarks-President-obama-and-prime-minister-abe-japan-hiroshima-peace |
| 200 | https://pib.gov.in/PressReleseDetailm.aspx?PRID=1591113 -> https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=1591113&reg=48&lang=2 |
| 200 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6945219/ |
| 200 | https://researchonline.lse.ac.uk/id/eprint/24786 |
| 200 | https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/may/doc2025512553601.pdf |
| 200 | https://tcdata.tzuchi-org.tw/files/public/public.test/2024/04/20231202-235718277-2980.pdf |
| 200 | https://ukraine.ohchr.org/en/Report-on-the-Human-Rights-Situation-in-Ukraine-1-June-30-November-2025 |
| 200 | https://unikorea.go.kr/web/eng_unikorea/bbs/bbs_0000000000000034/54268 |
| 200 | https://vn.usembassy.gov/fact-sheets-dioxin-remediation-at-bien-hoa-airbase-area/ |
| 200 | https://www.armscontrol.org/act/2013-07/news/nunn-lugar-program-scaled-back |
| 200 | https://www.cbsnews.com/news/quake-sorrow-unites-rivals/ |
| 200 | https://www.chinanews.com.cn/tw/tw-dlyw/news/2009/08-19/1824825.shtml |
| 403 | https://www.civilnet.am/en/news/691652/ |
| 200 | https://www.cmp-cyprus.org/press-release/the-government-of-ireland-donates-e30000-to-cmp/ |
| 200 | https://www.cna.com.tw/news/acn/202609020085.aspx |
| 403 | https://www.crisisgroup.org/alr/africa/ethiopia-eritrea/pulling-ethiopia-and-eritrea-back-from-war |
| 403 | https://www.defense.gov/News/News-Stories/Article/Article/1586122/us-receives-fallen-service-members-remains-from-north-korea/ |
| 200 | https://www.disasterdiplomacy.org/chinataiwan.html |
| 200 | https://www.disasterdiplomacy.org/greeceturkey.html |
| 200 | https://www.disasterdiplomacy.org/indiapakistan.html |
| 403 | https://www.dtra.mil/Missions/Partnering/Cooperative-Threat-Reduction-Program/ |
| 200 | https://www.ettoday.net/news/20180512/1168072.htm |
| 200 | https://www.fmprc.gov.cn/web/ziliao_674904/zt_674979/ywzt_675099/2008zt_675545/hjtdhhy_675549/200807/t20080708_7957901.shtml |
| 200 | https://www.globalsecurity.org/military/library/news/2003/12/mil-031229-afps01.htm |
| 200 | https://www.globalsecurity.org/wmd/library/news/pakistan/2005/pakistan-051116-voa02.htm |
| 200 | https://www.globalsecurity.org/wmd/library/news/taiwan/1999/990921-prc.htm |
| 200 | https://www.globalsecurity.org/wmd/library/news/taiwan/1999/991001.htm |
| 200 | https://www.globalsecurity.org/wmd/library/news/taiwan/2009/taiwan-090512-cna01.htm |
| 200 | https://www.globalsecurity.org/wmd/library/news/taiwan/2015/taiwan-151230-cna02.htm |
| 200 | https://www.gwytb.gov.cn/xwdt/xwfb/xwfbh/201101/t20110106_1679287.htm |
| 200 | https://www.gwytb.gov.cn/zt/zylszl/lhjl/la2008q/wangu/1st/201101/t20110108_1684732.htm |
| 200 | https://www.gwytb.gov.cn/zt/zylszl/tufashijian/201802/t20180208_11922853.htm |
| 200 | https://www.icrc.org/en/article/historical-timeline-icrc-geneva-conventions-korea |
| 200 | https://www.icrc.org/en/document/falkland-islands-islas-malvinas-humanitarian-plan-identify-argentine-soldiers-buried-darwin |
| 200 | https://www.icrc.org/en/document/falklandmalvinas-islands-icrc-presents-argentina-and-united-kingdom-results-humanitarian |
| 200 | https://www.insurancejournal.com/news/international/2003/12/31/35341.htm |
| 200 | https://www.ksat.com/news/world/2023/02/12/earthquake-diplomacy-greek-foreign-minister-visits-turkey/ |
| 200 | https://www.mfa.am/en/press-conference/2023/02/15/fms_armenia_t%C3%BCrkiye/11865 |
| 403 | https://www.mfa.gr/en/minister-of-foreign-affairs-nikos-dendias-interview-with-ta-nea-savvatokyriako-newspaper-and-journalist-alexandra-fotaki-18022023/ |
| 403 | https://www.mofa.go.jp/announce/announce/2008/5/1180016_1010.html |
| 403 | https://www.mofa.go.jp/j_info/visit/incidents/index2.html |
| 200 | https://www.nam.ac.uk/explore/christmas-ww1 |
| 200 | https://www.nasa.gov/history/45-years-ago-historic-handshake-in-space/ |
| 200 | https://www.nasa.gov/international-space-station/space-station-facts-and-figures/ |
| 200 | https://www.npr.org/sections/thetorch/2018/02/10/584749102/korean-womens-hockey-team-presents-a-unified-front-as-it-takes-to-the-ice |
| 200 | https://www.ofaj.org/institution/lhistoire-de-loffice-franco-allemand-pour-la-jeunesse |
| 200 | https://www.peaceagreements.org/agreements/2097/ |
| 200 | https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1589022 -> https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1589022&reg=48&lang=2 |
| 200 | https://www.rfa.org/mandarin/duomeiti/tebiejiemu/xch-03212023162857.html |
| 200 | https://www.sef.org.tw/article-1-106-667 |
| 200 | https://www.sef.org.tw/article-1-129-11224 |
| 200 | https://www.sef.org.tw/article-1-129-5867 |
| 200 | https://www.sef.org.tw/article-1-15-1366 |
| 200 | https://www.taipeitimes.com/News/front/archives/2017/05/23/2003671113 |
| 200 | https://www.theglobeandmail.com/news/world/india-pakistan-thaw-in-quakes-aftermath/article1030003/ |
| 200 | https://www.theparentscircle.org/en/about_eng-2/ |
| 200 | https://www.tribuneindia.com/news/delhi/dsgmc-writes-to-pm-modi-to-reopen-kartarpur-corridor-ahead-of-punjab-visit/ |
| 200 | https://www.un.org/en/black-sea-grain-initiative/achievements |
| 200 | https://www.un.org/en/black-sea-grain-initiative/update-15-july-2023 |
| 200 | https://www.worldbank.org/en/region/sar/brief/fact-sheet-the-indus-waters-treaty-1960-and-the-world-bank |
| 200 | https://www.worldjournal.com/wj/story/121220/8884050 |
| 200 | https://www.xinhuanet.com/english/bilingual/2016-06/29/c_135475576.htm |
| 200 | https://wwwnc.cdc.gov/eid/article/4/3/98-0018_article |

### Checker script (not committed separately; stdlib only)

```python
"""Validate bridges.json and check every source URL (stdlib only)."""
import json, sys, ssl, urllib.request, urllib.parse, collections
from concurrent.futures import ThreadPoolExecutor

KINDS = {"disaster-aid", "rescue", "statement", "cultural", "humanitarian", "economic", "personal", "institutional"}
CONF = {"ok", "check", "unconfirmed"}
KEYS = ["id", "pair", "sides", "year", "kind", "who", "title", "what", "why_it_matters", "src", "conf", "note"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

d = json.load(open(sys.argv[1], encoding="utf-8"))
assert set(d) == {"about", "verified", "stories"}, d.keys()
ids = [s["id"] for s in d["stories"]]
dups = [i for i, n in collections.Counter(ids).items() if n > 1]
assert not dups, dups
for s in d["stories"]:
    assert list(s) == KEYS, (s["id"], list(s))
    assert s["kind"] in KINDS and s["conf"] in CONF, s["id"]
    assert len(s["pair"]) == 2 and len(s["sides"]) == 2 and s["src"], s["id"]
    for r in s["src"]:
        assert set(r) == {"label", "url", "lang"} and r["url"].startswith("http"), s["id"]
print(f"schema OK: {len(ids)} stories, unique ids")

ctx = ssl.create_default_context()


def status(u):
    q = urllib.parse.urlsplit(u)
    u2 = urllib.parse.urlunsplit((q.scheme, q.netloc, urllib.parse.quote(q.path, safe="/%:@"), q.query, q.fragment))
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(u2, method=method, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
            with urllib.request.urlopen(req, timeout=30, context=ctx) as f:
                return f.status, f.geturl()
        except urllib.error.HTTPError as e:
            if method == "GET":
                return e.code, ""
        except Exception as e:
            if method == "GET":
                return "ERR " + type(e).__name__ + ": " + str(e)[:60], ""
    return "?", ""


urls = sorted({r["url"] for s in d["stories"] for r in s["src"]})
with ThreadPoolExecutor(8) as ex:
    res = dict(zip(urls, ex.map(status, urls)))
for u in urls:
    st, fu = res[u]
    redir = f" -> {fu}" if fu and fu.rstrip("/") != u.rstrip("/") else ""
    print(f"| {st} | {u}{redir} |")
```
