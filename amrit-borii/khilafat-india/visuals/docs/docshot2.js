const { chromium } = require('playwright');
const jobs = JSON.parse(require('fs').readFileSync(process.argv[2]));
const OUT = process.argv[3];
(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await browser.newContext({ viewport: { width: 760, height: 900 }, deviceScaleFactor: 3, ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  for (const j of jobs) {
    try {
      await page.goto(j.url, { waitUntil: 'networkidle', timeout: 90000 });
      await page.addStyleTag({ content: '.vector-sticky-header,#siteNotice,.mw-cookie-banner{display:none!important} sup.reference{font-size:70%}' });
      const res = await page.evaluate((j) => {
        const root = document.querySelector('#mw-content-text');
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        const nodes = []; let full = ''; let n;
        while ((n = walker.nextNode())) { nodes.push([n, full.length]); full += n.data; }
        const norm = s => s.replace(/[‘’]/g, "'").replace(/[“”]/g, '"');
        const F = norm(full);
        function mk(i, j2) {
          const r = document.createRange(); let ok1 = false;
          for (const [nd, off] of nodes) { if (!ok1 && off <= i && i <= off + nd.data.length) { r.setStart(nd, i - off); ok1 = true; } if (off <= j2 && j2 <= off + nd.data.length) { r.setEnd(nd, j2 - off); break; } }
          return r;
        }
        const si = F.indexOf(norm(j.start)); if (si < 0) return { err: 'start not found' };
        const ei = F.indexOf(norm(j.end), si); if (ei < 0) return { err: 'end not found' };
        const sx = window.scrollX, sy = window.scrollY;
        const abs = q => ({ x: q.left + sx, y: q.top + sy, w: q.width, h: q.height });
        const blk = r => abs((r.startContainer.parentElement.closest('p,li,dd,blockquote,td') || r.startContainer.parentElement).getBoundingClientRect());
        const b1 = blk(mk(si, si + 1)), b2 = blk(mk(ei, ei + j.end.length));
        const hls = j.hl.map(h => { const k = F.indexOf(norm(h), si); if (k < 0) return null; return Array.from(mk(k, k + h.length).getClientRects()).filter(q => q.width > 2).map(abs); });
        return { b1, b2, hls };
      }, j);
      if (res.err) { console.log(j.key, 'ERROR', res.err); continue; }
      const pad = 22;
      const x0 = Math.min(res.b1.x, res.b2.x) - pad, y0 = res.b1.y - pad;
      const x1 = Math.max(res.b1.x + res.b1.w, res.b2.x + res.b2.w) + pad, y1 = res.b2.y + res.b2.h + pad;
      await page.screenshot({ path: `${OUT}/${j.key}.png`, fullPage: true, clip: { x: x0, y: y0, width: x1 - x0, height: y1 - y0 } });
      const lines = res.hls.map(list => {
        if (!list) return null; const m = {};
        for (const q of list) { const k = Math.round(q.y); const l = m[k]; m[k] = l ? [Math.min(l[0], q.x), q.y, Math.max(l[2], q.x + q.w), Math.max(l[3], q.h)] : [q.x, q.y, q.x + q.w, q.h]; }
        return Object.values(m).sort((a, b) => a[1] - b[1]).map(v => ({ x0: (v[0] - x0) * 3, y: (v[1] - y0) * 3, x1: (v[2] - x0) * 3, h: v[3] * 3 }));
      });
      require('fs').writeFileSync(`${OUT}/${j.key}.json`, JSON.stringify({ url: j.url, title: j.title, lines, hl: j.hl }, null, 1));
      console.log(j.key, 'ok', Math.round(x1 - x0), 'x', Math.round(y1 - y0), 'missing hl:', lines.filter(l => !l).length);
    } catch (e) { console.log(j.key, 'EXC', e.message.slice(0, 120)); }
  }
  await browser.close();
})();
