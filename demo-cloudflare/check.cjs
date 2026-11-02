const { chromium, devices } = require(process.env.HOME + '/Documents/project-world-all-v1/common-ground/apps/home/node_modules/playwright');
(async () => {
  const url = process.argv[2];
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
  const p = await ctx.newPage(); const errs = [];
  p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  p.on('pageerror', e => errs.push('pageerror ' + e.message));
  const r = await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  const info = await p.evaluate(() => {
    const vis = id => { const el = document.getElementById(id); const r = el.getBoundingClientRect(); return { top: Math.round(r.top), h: Math.round(r.height), w: Math.round(r.width) }; };
    const canvasNonEmpty = id => { const c = document.getElementById(id); try { const d = document.createElement('canvas'); d.width = c.width; d.height = c.height; const x = d.getContext('2d'); x.drawImage(c, 0, 0); const px = x.getImageData(0, 0, d.width, d.height).data; let n = 0; for (let i = 0; i < px.length; i += 4) if (px[i] + px[i+1] + px[i+2] > 60) n++; return n; } catch (e) { return 'err ' + e.message; } };
    const small = [...document.querySelectorAll('a,button,[role=tab]')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.height < 24 || r.width < 24); }).map(e => (e.textContent||'').trim().slice(0,20) + ' ' + Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height));
    return { sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
      banner: document.querySelector('.demo-banner')?.textContent, bannerH: document.querySelector('.demo-banner')?.getBoundingClientRect().height,
      web: vis('web'), tri: vis('tri'), webPx: canvasNonEmpty('web'), triNodes: document.querySelectorAll('#tri *').length,
      peacePx: canvasNonEmpty('peace'), skyPx: canvasNonEmpty('sky'), smallTargets: small.length, smallSample: small.slice(0, 12) };
  });
  await p.screenshot({ path: 'shot-fold.png' });
  // tap test on tri and web
  await p.locator('#web').tap({ position: { x: 150, y: 150 } }).catch(e => errs.push('tap web ' + e.message));
  await p.locator('.demo-banner').evaluate(e => e.href).then(h => info.bannerHref = h);
  await p.screenshot({ path: 'shot-top.png' });
  await p.locator('#sec-ch').scrollIntoViewIfNeeded(); await p.waitForTimeout(500);
  await p.screenshot({ path: 'shot-ch.png' });
  console.log(JSON.stringify({ status: r.status(), ...info, errs }, null, 1));
  await b.close();
})();
