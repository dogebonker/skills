#!/usr/bin/env node
// A free, local, Mobbin-style library of real app screens, reused across projects.
// Needs Node 22+ (built-in fetch and WebSocket) and an installed Chrome. No npm packages.
//
//   node library.mjs appstore "<app name>" [--mac] [--flow store-listing]
//   node library.mjs login <url>                     sign in once on the library's own Chrome profile
//   node library.mjs capture <url> --app <name> --flow <flow> [--phone] [--full] [--logged-in] [--wait 1500] [--note "..."]
//   node library.mjs add <image file or URL...> --app <name> --flow <flow> --platform <web|web-phone|ios|ipad|mac|android> [--source <url>] [--note "..."]
//   node library.mjs search <words...>
//   node library.mjs gallery                         writes <library>/index.html
//
// Desktop captures are 1440x900. --phone is 390x844 at 2x (780px wide files). --full captures up to 8000px tall.
// Library root: $DESIGN_LIBRARY (default ~/.design-library). Never point it at a synced or committed folder.
// Login profile: $UI_BENCHMARK_PROFILE (default ~/.cache/ui-benchmark/chrome-profile), kept outside the library.
// Chrome binary: $CHROME.
import { mkdirSync, readFileSync, writeFileSync, renameSync, existsSync, mkdtempSync, rmSync, chmodSync, readdirSync } from 'node:fs';
import { join, extname, relative, resolve, basename } from 'node:path';
import { homedir, tmpdir } from 'node:os';
import { spawn } from 'node:child_process';

const ROOT = process.env.DESIGN_LIBRARY || join(homedir(), '.design-library');
const DB = join(ROOT, 'library.json');
const PROFILE = process.env.UI_BENCHMARK_PROFILE || join(homedir(), '.cache', 'ui-benchmark', 'chrome-profile');
const CHROME = process.env.CHROME || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].find(existsSync) || 'google-chrome';
const PHONE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';
const PLATFORMS = ['web', 'web-phone', 'ios', 'ipad', 'mac', 'android'];
const IMAGE_EXT = ['.png', '.jpg', '.jpeg', '.webp', '.gif'];
const BOOL = new Set(['mac', 'phone', 'full', 'logged-in']);

const sleep = ms => new Promise(r => setTimeout(r, ms));
// Resolves or rejects with p, or rejects after ms, and always clears its timer so the process can exit.
const within = (p, ms, what) => new Promise((ok, fail) => {
  const t = setTimeout(() => fail(new Error(`${what} timed out after ${ms / 1000}s`)), ms);
  p.then(v => { clearTimeout(t); ok(v); }, e => { clearTimeout(t); fail(e); });
});
const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'x';
const load = () => (existsSync(DB) ? JSON.parse(readFileSync(DB, 'utf8')) : []);

function parse(argv) {
  const pos = [], opt = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) { pos.push(argv[i]); continue; }
    const k = argv[i].slice(2);
    if (BOOL.has(k)) { opt[k] = true; continue; }
    if (argv[i + 1] === undefined || argv[i + 1].startsWith('--')) throw new Error(`--${k} needs a value`);
    opt[k] = argv[++i];
  }
  return { pos, opt };
}

// Serialises index updates across parallel processes with an exclusive lock file.
// A lock older than 10s is treated as left behind by a crashed run and broken.
function withLock(fn) {
  mkdirSync(ROOT, { recursive: true });
  const lock = DB + '.lock';
  const pause = new Int32Array(new SharedArrayBuffer(4));
  for (let i = 0; ; i++) {
    try { writeFileSync(lock, String(process.pid), { flag: 'wx' }); break; } catch (e) { if (e.code !== 'EEXIST') throw e; }
    if (i === 400) rmSync(lock, { force: true });
    Atomics.wait(pause, 0, 0, 25);
  }
  try { return fn(); } finally { rmSync(lock, { force: true }); }
}

// Writes the image under <root>/<app>/<flow>/<platform>-<n><ext> and adds it to the index.
// Numbers never repeat (past the highest file or index entry), and 'wx' refuses to overwrite,
// so deletions and parallel captures can't clobber a screen.
function record(bytes, ext, meta) {
  withLock(() => {
    const platform = slug(meta.platform);
    const dir = join(ROOT, slug(meta.app), slug(meta.flow));
    mkdirSync(dir, { recursive: true });
    const db = load();
    const seen = [...readdirSync(dir), ...db.filter(e => e.file.startsWith(dir + '/')).map(e => basename(e.file))];
    let n = Math.max(0, ...seen.map(f => Number(f.match(new RegExp(`^${platform}-(\\d+)\\.`))?.[1] || 0))) + 1;
    let file;
    for (;; n++) {
      file = join(dir, `${platform}-${n}${ext}`);
      try { writeFileSync(file, bytes, { flag: 'wx' }); break; } catch (e) { if (e.code !== 'EEXIST') throw e; }
    }
    db.push({ file, ...meta, platform, captured: new Date().toISOString().slice(0, 10) });
    writeFileSync(DB + '.tmp', JSON.stringify(db, null, 2) + '\n');
    renameSync(DB + '.tmp', DB);
    console.log(file);
  });
}

async function download(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
}

async function appstore(term, opt) {
  const entity = opt.mac ? 'macSoftware' : 'software';
  const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(term)}&entity=${entity}&limit=1`);
  if (!res.ok) throw new Error(`App Store search failed: HTTP ${res.status}`);
  const app = (await res.json()).results?.[0];
  if (!app) throw new Error(`no App Store match for "${term}"`);
  const have = new Set(load().map(e => e.image));
  const shots = [...(app.screenshotUrls || []).map(u => [u, opt.mac ? 'mac' : 'ios']), ...(app.ipadScreenshotUrls || []).map(u => [u, 'ipad'])];
  for (const [u, platform] of shots) {
    // The image server renders any size: ask for full width instead of the 320px thumbnail.
    const image = u.replace(/\/\d+x\d+[a-z]*\.(jpg|png|webp)$/, '/1290x0w.$1');
    if (have.has(image)) continue;
    record(await download(image), extname(new URL(image).pathname) || '.jpg', {
      app: app.trackName, flow: opt.flow || 'store-listing', platform, source: app.trackViewUrl, image,
      note: 'App Store marketing screenshot: staged, not a real flow',
    });
  }
}

function launch(args) {
  const proc = spawn(CHROME, args, { stdio: 'ignore' });
  proc.done = new Promise(r => { proc.once('exit', r); proc.once('error', e => { proc.failed = e; r(); }); });
  return proc;
}

async function stop(proc) {
  if (proc.failed || proc.exitCode !== null || proc.signalCode !== null) return;
  proc.kill();
  await within(proc.done, 5000, 'Chrome exit').catch(() => proc.kill('SIGKILL'));
}

function useProfile() {
  mkdirSync(PROFILE, { recursive: true });
  chmodSync(PROFILE, 0o700);
  return PROFILE;
}

// Drives headless Chrome over the DevTools protocol: real viewport sizes, phone emulation, full page.
async function shoot(url, opt) {
  const loggedIn = opt['logged-in'];
  if (loggedIn && !/^https?:/.test(url)) throw new Error('--logged-in only loads http(s) URLs');
  const profile = loggedIn ? useProfile() : mkdtempSync(join(tmpdir(), 'ui-benchmark-chrome-'));
  // Port 0 lets Chrome pick a free port and write it to DevToolsActivePort, so we never attach to another browser.
  const portFile = join(profile, 'DevToolsActivePort');
  rmSync(portFile, { force: true });
  const chrome = launch(['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', 'about:blank']);
  let ws;
  try {
    let port;
    for (let i = 0; i < 150 && !port; i++) {
      if (chrome.failed) throw new Error(`Chrome not found at ${CHROME}. Set CHROME to its binary.`);
      if (chrome.exitCode !== null) throw new Error(loggedIn ? 'Chrome quit at once: the login window is probably still open. Quit it and retry.' : 'Chrome quit at once.');
      if (existsSync(portFile)) port = readFileSync(portFile, 'utf8').split('\n')[0].trim();
      if (!port) await sleep(100);
    }
    if (!port) throw new Error('Chrome did not start within 15s');
    const page = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page');
    ws = new WebSocket(page.webSocketDebuggerUrl);
    await within(new Promise((ok, fail) => { ws.onopen = ok; ws.onerror = () => fail(new Error('DevTools connection failed')); }), 10000, 'DevTools connection');
    let id = 0, onLoad;
    const pending = new Map();
    ws.onmessage = m => {
      const d = JSON.parse(m.data);
      if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
      if (d.method === 'Page.loadEventFired') onLoad?.();
    };
    ws.onclose = () => { for (const done of pending.values()) done({ error: { message: 'Chrome closed the connection' } }); pending.clear(); };
    const send = (method, params = {}) => within(new Promise((ok, fail) => {
      const i = ++id;
      pending.set(i, d => (d.error ? fail(new Error(`${method}: ${d.error.message}`)) : ok(d.result)));
      ws.send(JSON.stringify({ id: i, method, params }));
    }), 30000, method);

    await send('Page.enable');
    const [width, height, scale] = opt.phone ? [390, 844, 2] : [1440, 900, 1];
    await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: scale, mobile: !!opt.phone });
    if (opt.phone) await send('Emulation.setUserAgentOverride', { userAgent: PHONE_UA });
    const loaded = new Promise(r => { onLoad = r; });
    const nav = await send('Page.navigate', { url });
    if (nav.errorText) throw new Error(`could not load ${url}: ${nav.errorText}`);
    await within(loaded, 20000, 'page load').catch(() => console.error('warning: page never finished loading; capturing what rendered'));
    const wait = Number(opt.wait ?? 1500);
    if (!Number.isFinite(wait) || wait < 0) throw new Error('--wait takes milliseconds');
    await sleep(wait);
    const final = (await send('Runtime.evaluate', { expression: 'location.href', returnByValue: true })).result.value;
    let clip;
    if (opt.full) {
      const { cssContentSize: s } = await send('Page.getLayoutMetrics');
      // ponytail: 8000px cap keeps endless feeds from producing huge files; raise it if a long page gets cut.
      clip = { x: 0, y: 0, width, height: Math.min(Math.ceil(s.height), 8000), scale: 1 };
    }
    const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: !!opt.full, ...(clip && { clip }) });
    return { bytes: Buffer.from(data, 'base64'), final };
  } finally {
    ws?.close();
    await stop(chrome);
    if (!loggedIn) rmSync(profile, { recursive: true, force: true });
  }
}

// Ignores query and hash, so tracking parameters don't count as a redirect.
const samePage = (a, b) => { const x = new URL(a), y = new URL(b); return x.origin === y.origin && x.pathname.replace(/\/$/, '') === y.pathname.replace(/\/$/, ''); };

function gallery() {
  const items = load().filter(e => existsSync(e.file)).map(e => ({ ...e, src: relative(ROOT, e.file).split('/').map(encodeURIComponent).join('/') }));
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Screen library</title><style>
:root { --bg: #f7f7f5; --panel: #fff; --ink: #1a1a19; --muted: #6b6a66; --line: #e6e5e1; }
@media (prefers-color-scheme: dark) { :root { --bg: #121211; --panel: #1b1b1a; --ink: #f2f1ee; --muted: #a09f9a; --line: #2c2c2a; } }
* { box-sizing: border-box; } body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.5 system-ui, sans-serif; }
main { max-width: 1400px; margin: 0 auto; padding: 20px 16px 48px; }
.bar { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 20px; position: sticky; top: 0; background: var(--bg); padding: 8px 0; }
input, select { font: inherit; color: inherit; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 6px 10px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
figure { margin: 0; background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
figure img { width: 100%; height: 260px; object-fit: cover; object-position: top; display: block; background: var(--line); }
figcaption { padding: 8px 10px; font-size: 13px; } figcaption span { color: var(--muted); display: block; }
a { color: inherit; }
</style></head><body><main><h1>Screen library</h1><div class="bar">
<input id="q" type="search" placeholder="Search app, flow, note" aria-label="Search">
<select id="app" aria-label="App"><option value="">All apps</option></select>
<select id="flow" aria-label="Flow"><option value="">All flows</option></select>
<select id="platform" aria-label="Platform"><option value="">All platforms</option></select>
<span id="count"></span></div><div class="grid" id="grid"></div></main>
<script>
const items = ${JSON.stringify(items).replace(/</g, '\\u003c')};
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
for (const k of ['app', 'flow', 'platform']) for (const v of [...new Set(items.map(i => i[k]))].sort()) document.getElementById(k).append(new Option(v, v));
function draw() {
  const q = document.getElementById('q').value.toLowerCase();
  const f = k => document.getElementById(k).value;
  const shown = items.filter(i => (!f('app') || i.app === f('app')) && (!f('flow') || i.flow === f('flow')) && (!f('platform') || i.platform === f('platform'))
    && (!q || [i.app, i.flow, i.platform, i.note, i.source].join(' ').toLowerCase().includes(q)));
  document.getElementById('count').textContent = shown.length + ' screens';
  document.getElementById('grid').innerHTML = shown.map(i => '<figure><a href="' + esc(i.src) + '" target="_blank"><img loading="lazy" src="' + esc(i.src) + '" alt="' + esc(i.app + ', ' + i.flow) + '"></a><figcaption><b>' + esc(i.app) + '</b> · ' + esc(i.flow) + '<span>' + esc(i.platform) + ' · ' + esc(i.captured) + (i.note ? ' · ' + esc(i.note) : '') + '</span></figcaption></figure>').join('');
}
for (const id of ['q', 'app', 'flow', 'platform']) document.getElementById(id).oninput = draw;
draw();
</script></body></html>
`;
  mkdirSync(ROOT, { recursive: true });
  writeFileSync(join(ROOT, 'index.html'), html);
  console.log(join(ROOT, 'index.html'), `(${items.length} screens)`);
}

const need = (opt, ...keys) => { for (const k of keys) if (!opt[k]) throw new Error(`--${k} is required`); };
try {
  const [cmd, ...rest] = process.argv.slice(2);
  const { pos, opt } = parse(rest);
  if (cmd === 'appstore' && pos[0]) await appstore(pos.join(' '), opt);
  else if (cmd === 'login' && pos[0]) {
    if (!/^https?:/.test(pos[0])) throw new Error('login takes an http(s) URL');
    rmSync(join(useProfile(), 'DevToolsActivePort'), { force: true });
    launch([`--user-data-dir=${PROFILE}`, '--no-first-run', '--no-default-browser-check', pos[0]]).unref();
    console.log('Sign in, then quit that Chrome completely (Cmd+Q on macOS). Captures with --logged-in reuse the session.');
  } else if (cmd === 'capture' && pos[0]) {
    need(opt, 'app', 'flow');
    const { bytes, final } = await shoot(pos[0], opt);
    let note = opt.note || '';
    if (!samePage(pos[0], final)) {
      console.error(`warning: ended on ${final}, not ${pos[0]}. Check it isn't a sign-in or error page.`);
      note = [note, `redirected to ${final}`].filter(Boolean).join('; ');
    }
    record(bytes, '.png', { app: opt.app, flow: opt.flow, platform: opt.phone ? 'web-phone' : 'web', source: pos[0], note });
  } else if (cmd === 'add' && pos.length) {
    need(opt, 'app', 'flow', 'platform');
    if (!PLATFORMS.includes(opt.platform)) throw new Error(`--platform must be one of ${PLATFORMS.join(', ')}`);
    for (const f of pos) {
      const remote = /^https?:/.test(f);
      const ext = extname(remote ? new URL(f).pathname : f).toLowerCase();
      if (!IMAGE_EXT.includes(ext)) throw new Error(`${f}: not an image (${IMAGE_EXT.join(', ')})`);
      record(remote ? await download(f) : readFileSync(resolve(f)), ext, {
        app: opt.app, flow: opt.flow, platform: opt.platform, source: opt.source || (remote ? f : 'user screenshot'), note: opt.note || '',
      });
    }
  } else if (cmd === 'search') {
    const words = pos.map(w => w.toLowerCase());
    for (const e of load().filter(e => words.every(w => [e.app, e.flow, e.platform, e.note, e.source].join(' ').toLowerCase().includes(w))))
      console.log(`${e.app} | ${e.flow} | ${e.platform} | ${e.captured} | ${e.file}`);
  } else if (cmd === 'gallery') gallery();
  else { console.error(readFileSync(new URL(import.meta.url), 'utf8').split('\n').filter(l => l.startsWith('//')).join('\n')); process.exitCode = 2; }
} catch (e) { console.error(`error: ${e.message}`); process.exitCode = 1; }
