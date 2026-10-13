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
