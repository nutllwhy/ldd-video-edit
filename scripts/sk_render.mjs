// 素描本镜头渲染器：Chrome 逐帧 window.render(t) 截图 → ffmpeg
//   出片：node sk_render.mjs <shot.html> <out.mp4>
//   静帧：node sk_render.mjs <shot.html> /tmp/前缀 0.5,2,4.9      → /tmp/前缀_0.5.png …
// 时长读页面 window.DUR，画布读 window.W / window.H（SK.mount 会设）。30fps。
// 依赖：playwright-core（可用 PLAYWRIGHT_DIR / HYPERFRAMES_DIR 指定）+ Playwright Chromium（可用 CHROME 覆盖）
// 机器慢时可用 perl 套超时：perl -e 'alarm 600; exec @ARGV' node sk_render.mjs …（浏览器偶尔启动卡住，可结束本次渲染后重跑）
import { createRequire } from 'module'; import { spawn, execSync } from 'child_process'; import path from 'path';
function loadPW() {
  const tries = [process.env.PLAYWRIGHT_DIR, process.env.HYPERFRAMES_DIR, process.cwd()];
  try { tries.push(execSync('npm root -g').toString().trim().replace(/\/node_modules$/, '')); } catch {}
  for (const d of tries.filter(Boolean)) {
    try { return createRequire(path.join(d, 'package.json'))('playwright-core'); } catch {}
  }
  console.error('找不到 playwright-core：npm i -D playwright-core，或设 PLAYWRIGHT_DIR'); process.exit(2);
}
const { chromium } = loadPW();
const launchOptions = { args: ['--allow-file-access-from-files'] };
if (process.env.CHROME) launchOptions.executablePath = process.env.CHROME;
const [html, out, stills] = process.argv.slice(2);
if (!html || !out) { console.error('usage: node sk_render.mjs <shot.html> <out.mp4 | 前缀> [t1,t2,…]'); process.exit(1); }
const b = await chromium.launch(launchOptions);
const probe = await b.newPage();
await probe.goto('file://' + path.resolve(html)); await probe.waitForLoadState('load');
const [W, H] = await probe.evaluate(() => [window.W || 1080, window.H || 1920]); await probe.close();
const p = await b.newPage({ viewport: { width: W, height: H } });
await p.goto('file://' + path.resolve(html)); await p.waitForLoadState('load');
await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
const D = await p.evaluate(() => window.DUR);
if (!D) { console.error('页面没有 window.DUR：最后要调用 SK.mount(tl, D)'); process.exit(1); }
if (stills) {
  for (const t of stills.split(',')) { await p.evaluate(x => window.render(x), +t); await p.screenshot({ path: `${out}_${t}.png` }); }
} else {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-r', '30', out]);
  const n = Math.round(D * 30);
  for (let f = 0; f < n; f++) { await p.evaluate(x => window.render(x), f / 30); ff.stdin.write(await p.screenshot({ type: 'jpeg', quality: 95 })); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await b.close(); console.log('done', out, D, `${W}x${H}`);
