import re, pathlib, sys
src = pathlib.Path.home()/"Documents/project-world-all-v1/triad-signal-atlas/site/index.html"
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
h = src.read_text()
def grab(id_):
    global h
    m = re.search(r'  <section id="%s".*?</section>\n\n?' % id_, h, re.S)
    h = h[:m.start()] + h[m.end():]
    return m.group(0)
web, ch = grab("sec-web"), grab("sec-ch")
i = h.index('  <section id="sec-peace"')
h = h[:i] + web + "\n" + ch + "\n" + h[i:]
# nav order: powers web, channels first
nav = re.search(r'<a href="#sec-peace">Peace Lab</a><a href="#sec-sky">Sources</a><a href="#sec-ch">Channels</a><a href="#sec-web">Powers web</a>', h)
h = h.replace(nav.group(0), '<a href="#sec-web">Powers web</a><a href="#sec-ch">Channels</a><a href="#sec-peace">Peace Lab</a><a href="#sec-sky">Sources</a>')
h = h.replace('<link rel="canonical" href="https://datazen123.github.io/triad-signal-atlas/">', '<meta name="robots" content="noindex">')
css = """<style id="demo-css">
.demo-banner{position:sticky;top:0;z-index:1000;display:block;margin:0;padding:6px 12px;font:600 12px/1.35 system-ui,sans-serif;text-align:center;background:#f5c542;color:#1a1300;text-decoration:none;min-height:24px}
.demo-banner u{white-space:nowrap}
@media (max-width:600px){
 header.top .lede{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
 header.top .eyebrow{display:none}
 #sec-web .sec-head p,#sec-ch .sec-head p{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
 #sec-web{display:flex;flex-direction:column}
 #sec-web>.sec-head{order:0} #sec-web>.observatory{order:1} #sec-web>.timebar{order:2;margin-top:10px} #sec-web>#layerChips{order:3} #sec-web>#webLegend{order:4}
 header.top .jump{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch}
 #sec-web .sec-head p.open,#sec-ch .sec-head p.open{display:block}
}
@media (pointer:coarse){main a,.wrap a,.side a{padding-block:4px}}
</style>
<script>document.addEventListener('click',e=>{const p=e.target.closest('#sec-web .sec-head p,#sec-ch .sec-head p');if(p)p.classList.toggle('open')});</script>
</head>"""
h = h.replace("</head>", css, 1)
h = h.replace("<body>", '<body>\n<a class="demo-banner" href="https://idea-trail.pages.dev" role="note">Demo · under construction. Data and methods are still being checked. <u>Idea Trail ↗</u></a>', 1)
(out/"index.html").write_text(h)
(out/"_headers").write_text("""/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Cross-Origin-Opener-Policy: same-origin
  X-Robots-Tag: noindex
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'
""")
print("ok", len(h))
