const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [seg, w, h, outDir] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5]];
  const frames = JSON.parse(fs.readFileSync('host_frames.json'))[seg];
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.goto(`http://127.0.0.1:8765/host/host.html?w=${w}&h=${h}`);
  await page.waitForFunction(() => window.__ready && window.__logo && window.__mon, null, { timeout: 60000 });
  const t0 = Date.now(); let i = 0;
  for (const fr of frames) {
    const p = `${outDir}/f${String(fr.f).padStart(6, '0')}.jpg`;
    if (!fs.existsSync(p)) { await page.evaluate(s => window.renderFrame(s), fr); await page.screenshot({ path: p, type: 'jpeg', quality: 95 }); }
    if (++i % 120 === 0) console.log(seg, i, '/', frames.length, ((Date.now() - t0) / i).toFixed(0), 'ms/f');
  }
  console.log(seg, 'done', ((Date.now() - t0) / 1000).toFixed(0), 's');
  await browser.close();
})();
