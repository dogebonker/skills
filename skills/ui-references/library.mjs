#!/usr/bin/env node
// A free, local, Mobbin-style library of real app screens, reused across projects, plus the captures and the
// design-kit check that a UI hill climb needs. Needs Node 22+ (built-in fetch and WebSocket) and an installed Chrome. No npm packages.
//
//   node library.mjs appstore "<app name>" [--mac] [--flow store-listing]
//   node library.mjs login <url>                     sign in once on the library's own Chrome profile
//   node library.mjs capture <url> --app <name> --flow <flow> [--phone] [--full] [--selector <css>] [--mono] [--logged-in] [--wait 1500] [--note "..."]
//   node library.mjs capture <url> --out <file.png> [same options]     writes one file and leaves the library alone (the target's climb rounds)
//   node library.mjs add <image file or URL...> --app <name> --flow <flow> --platform <web|web-phone|ios|ipad|mac|android> [--source <url>] [--note "..."]
//   node library.mjs mono <image...>                 writes <name>.mono.png beside each image: grayscale, so layout compares without brand colour
//   node library.mjs tokens <url> --from <design kit files...> [--selector <css>] [--phone] [--run "<js>"] [--logged-in]
//   node library.mjs search <words...>
//   node library.mjs gallery                         writes <library>/index.html
//
// Desktop captures are 1440x900. --phone is 390x844 at 2x (780px wide files). --full captures up to 8000px tall.
// --selector crops to the first element that matches. --run evaluates JS after load (open a menu, switch a tab).
// With --logged-in, --run only works on a local dev server (localhost), so it never clicks inside a signed-in product.
// tokens lists every rendered colour and font that the design kit files don't contain, and exits 1 when there are any.
// Give tokens the same --selector, --phone, --run and --logged-in as the capture it gates.
// Library root: $DESIGN_LIBRARY (default ~/.design-library). Never point it at a synced or committed folder.
// Login profile: $UI_BENCHMARK_PROFILE (default ~/.cache/ui-benchmark/chrome-profile), kept outside the library.
// Chrome binary: $CHROME.
import { mkdirSync, readFileSync, writeFileSync, renameSync, existsSync, mkdtempSync, rmSync, chmodSync, readdirSync } from 'node:fs';
import { join, extname, relative, resolve, basename, dirname } from 'node:path';
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
const MIME = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif' };
const BOOL = new Set(['mac', 'phone', 'full', 'logged-in', 'mono']);
const LIST = new Set(['from']);

const sleep = ms => new Promise(r => setTimeout(r, ms));
// Resolves or rejects with p, or rejects after ms, and always clears its timer so the process can exit.
const within = (p, ms, what) => new Promise((ok, fail) => {
  const t = setTimeout(() => fail(new Error(`${what} timed out after ${ms / 1000}s`)), ms);
  p.then(v => { clearTimeout(t); ok(v); }, e => { clearTimeout(t); fail(e); });
});
const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'x';
const load = () => (existsSync(DB) ? JSON.parse(readFileSync(DB, 'utf8')) : []);

// --from takes every following word up to the next --option, so a shell glob works.
function parse(argv) {
  const pos = [], opt = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) { pos.push(argv[i]); continue; }
    const k = argv[i].slice(2);
    if (BOOL.has(k)) { opt[k] = true; continue; }
    if (argv[i + 1] === undefined || argv[i + 1].startsWith('--')) throw new Error(`--${k} needs a value`);
    if (LIST.has(k)) { opt[k] = []; while (argv[i + 1] !== undefined && !argv[i + 1].startsWith('--')) opt[k].push(argv[++i]); continue; }
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
  return withLock(() => {
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
    return file;
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

// Starts headless Chrome, hands fn a DevTools `send` plus an `evaluate` helper, and always cleans up.
async function withChrome(loggedIn, fn) {
  const profile = loggedIn ? useProfile() : mkdtempSync(join(tmpdir(), 'ui-references-chrome-'));
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
    let id = 0;
    const pending = new Map(), events = {};
    ws.onmessage = m => {
      const d = JSON.parse(m.data);
      if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
      if (d.method) events[d.method]?.();
    };
    ws.onclose = () => { for (const done of pending.values()) done({ error: { message: 'Chrome closed the connection' } }); pending.clear(); };
    const send = (method, params = {}) => within(new Promise((ok, fail) => {
      const i = ++id;
      pending.set(i, d => (d.error ? fail(new Error(`${method}: ${d.error.message}`)) : ok(d.result)));
      ws.send(JSON.stringify({ id: i, method, params }));
    }), 30000, method);
    const evaluate = async expression => {
      const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
      return r.result.value;
    };
    const once = name => new Promise(r => { events[name] = r; });
    return await fn({ send, evaluate, once });
  } finally {
    ws?.close();
    await stop(chrome);
    if (!loggedIn) rmSync(profile, { recursive: true, force: true });
  }
}

// Checked before Chrome starts. --run clicks, so with a signed-in profile it only runs on our own local dev server.
function guard(url, opt) {
  if (opt['logged-in'] && !/^https?:/.test(url)) throw new Error('--logged-in only loads http(s) URLs');
  if (opt['logged-in'] && opt.run && !/^(localhost|127\.0\.0\.1|\[::1\]|.+\.localhost)$/.test(new URL(url).hostname))
    throw new Error('--run with --logged-in only works on a local dev server: never click inside a signed-in product');
}

const warnRedirect = (url, final) => {
  if (samePage(url, final)) return false;
  console.error(`warning: ended on ${final}, not ${url}. Check it isn't a sign-in or error page.`);
  return true;
};

// Opens url at the capture size, waits, runs --run, and returns the size and the final URL.
async function open({ send, evaluate, once }, url, opt) {
  await send('Page.enable');
  const [width, height, scale] = opt.phone ? [390, 844, 2] : [1440, 900, 1];
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: scale, mobile: !!opt.phone });
  if (opt.phone) await send('Emulation.setUserAgentOverride', { userAgent: PHONE_UA });
  const loaded = once('Page.loadEventFired');
  const nav = await send('Page.navigate', { url });
  if (nav.errorText) throw new Error(`could not load ${url}: ${nav.errorText}`);
  await within(loaded, 20000, 'page load').catch(() => console.error('warning: page never finished loading; capturing what rendered'));
  const wait = Number(opt.wait ?? 1500);
  if (!Number.isFinite(wait) || wait < 0) throw new Error('--wait takes milliseconds');
  await sleep(wait);
  if (opt.run) { await evaluate(`(async () => { ${opt.run} })()`); await sleep(wait); }
  return { width, final: await evaluate('location.href') };
}

const box = sel => `(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null;
  const r = e.getBoundingClientRect(); return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height }; })()`;

// Drives headless Chrome over the DevTools protocol: real viewport sizes, phone emulation, full page, one element.
async function shoot(url, opt) {
  guard(url, opt);
  return withChrome(opt['logged-in'], async c => {
    const { width, final } = await open(c, url, opt);
    if (opt.mono) await c.evaluate(`document.documentElement.style.filter = 'grayscale(1)'`);
    let clip;
    if (opt.selector) {
      const b = await c.evaluate(box(opt.selector));
      if (!b || !b.width || !b.height) throw new Error(`--selector ${opt.selector} matched nothing visible`);
      clip = { ...b, scale: 1 };
    } else if (opt.full) {
      const { cssContentSize: s } = await c.send('Page.getLayoutMetrics');
      // ponytail: 8000px cap keeps endless feeds from producing huge files; raise it if a long page gets cut.
      clip = { x: 0, y: 0, width, height: Math.min(Math.ceil(s.height), 8000), scale: 1 };
    }
    const { data } = await c.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: !!clip, ...(clip && { clip }) });
    return { bytes: Buffer.from(data, 'base64'), final };
  });
}

// Grayscale copy of each image, drawn through a canvas from a data URL so nothing is tainted.
async function mono(files) {
  await withChrome(false, async ({ evaluate }) => {
    for (const f of files.filter(f => !f.endsWith('.mono.png'))) {
      const ext = extname(f).toLowerCase();
      if (!MIME[ext]) throw new Error(`${f}: not an image (${IMAGE_EXT.join(', ')})`);
      const url = `data:${MIME[ext]};base64,${readFileSync(resolve(f)).toString('base64')}`;
      const out = await evaluate(`new Promise((ok, fail) => { const i = new Image(); i.onerror = () => fail(new Error('image did not decode'));
        i.onload = () => { const c = document.createElement('canvas'); c.width = i.naturalWidth; c.height = i.naturalHeight;
          const x = c.getContext('2d'); x.filter = 'grayscale(1)'; x.drawImage(i, 0, 0); ok(c.toDataURL('image/png').split(',')[1]); };
        i.src = ${JSON.stringify(url)}; })`);
      const file = join(dirname(resolve(f)), basename(f, extname(f)) + '.mono.png');
      writeFileSync(file, Buffer.from(out, 'base64'));
      console.log(file);
    }
  });
}

// Every rendered colour and font on the page (pseudo-elements, form controls and open shadow roots included),
// checked against the design kit files. Colours compare as opaque sRGB, so a brand colour at any alpha passes.
// Chrome parses both sides: hex, rgb, hsl, oklch, named colours given as a value, and bare shadcn/Tailwind channels (--x: 222 84% 5%).
// Fonts pass when the declared family is named in the kit and the font Chrome actually renders is too.
const COLOR = /#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\([^()]*\)/gi;
const BARE_HSL = /--[\w-]+\s*:\s*(-?[\d.]+(?:deg)?\s+[\d.]+%\s+[\d.]+%)\s*[;}\n]/g;
const BARE_RGB = /--[\w-]+\s*:\s*(\d{1,3}\s+\d{1,3}\s+\d{1,3})\s*[;}\n]/g;
const GENERIC = new Set(['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'ui-sans-serif', 'ui-serif', 'ui-monospace', '-apple-system', 'blinkmacsystemfont']);
async function tokens(url, opt) {
  if (!opt.from?.length) throw new Error('--from needs the design kit files: DESIGN.md, the tokens CSS, the Tailwind theme');
  guard(url, opt);
  const kit = opt.from.map(f => readFileSync(resolve(f), 'utf8')).join('\n');
  const lower = kit.toLowerCase();
  const kitColors = [...new Set([
    ...(kit.match(COLOR) || []),
    ...[...kit.matchAll(BARE_HSL)].map(m => `hsl(${m[1]})`),
    ...[...kit.matchAll(BARE_RGB)].map(m => `rgb(${m[1]})`),
  ])];
  // Named colours count only as a value (--x: white; or surface: white), never from prose like "avoid red".
  const kitWords = [...new Set([...lower.matchAll(/:\s*([a-z]{3,20})\s*(?:[;},]|$)/gm)].map(m => m[1]))];
  const inKit = name => new RegExp(`(^|[^a-z0-9])${name.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^a-z0-9])`).test(lower);
  const found = await withChrome(opt['logged-in'], async c => {
    const { final } = await open(c, url, opt);
    warnRedirect(url, final);
    const page = await c.evaluate(`(() => {
      const probe = document.createElement('i'); document.body.append(probe);
      const cv = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
      // Opaque sRGB bytes for any CSS colour, or null for a transparent or unparseable one.
      const rgb = c => {
        probe.style.color = ''; probe.style.color = c; if (!probe.style.color) return null;
        const px = () => { cv.clearRect(0, 0, 1, 1); cv.fillStyle = 'rgba(0, 0, 0, 0)'; cv.fillStyle = getComputedStyle(probe).color; cv.fillRect(0, 0, 1, 1); return cv.getImageData(0, 0, 1, 1).data; };
        if (px()[3] === 0) return null;
        probe.style.color = 'rgb(from ' + c + ' r g b)';
        return [...px().slice(0, 3)];
      };
      const skip = new Set(['transparent', 'currentcolor', 'inherit', 'initial', 'unset', 'revert', 'none']);
      const named = ${JSON.stringify(kitWords)}.filter(w => !skip.has(w) && CSS.supports('color', w));
      const kit = [...${JSON.stringify(kitColors)}, ...named].map(rgb).filter(Boolean);
      const start = ${opt.selector ? `document.querySelector(${JSON.stringify(opt.selector)})` : 'document.documentElement'};
      if (!start) throw new Error('selector matched nothing');
      const all = function* (e) { yield e; if (e.shadowRoot) for (const c of e.shadowRoot.children) yield* all(c); for (const c of e.children) yield* all(c); };
      const SHAPES = new Set(['path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'tspan', 'use']);
      const FIELDS = new Set(['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON']);
      const colors = {}, fonts = {};
      const name = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\\s+/).slice(0, 2).join('.') : '');
      const note = (k, where) => { (colors[k] ??= { n: 0, where }).n++; };
      const check = (s, where, text, svg) => {
        const props = ['background-color'];
        if (text) props.push('color');
        for (const side of ['top', 'right', 'bottom', 'left']) if (parseFloat(s['border-' + side + '-width']) > 0 && s['border-' + side + '-style'] !== 'none') props.push('border-' + side + '-color');
        if (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) props.push('outline-color');
        if (svg) props.push('fill', 'stroke');
        const values = props.map(p => [p, s.getPropertyValue(p)]);
        for (const g of (s.backgroundImage.match(${COLOR}) || [])) values.push(['background-image', g]);
        for (const g of (s.boxShadow === 'none' ? [] : s.boxShadow.match(${COLOR}) || [])) values.push(['box-shadow', g]);
        for (const [p, v] of values) {
          const c = rgb(v); if (!c) continue;
          if (kit.some(k => k.every((x, i) => Math.abs(x - c[i]) <= 2))) continue;
          note('#' + c.map(x => x.toString(16).padStart(2, '0')).join(''), where + ' ' + p);
        }
      };
      for (const e of all(start)) {
        if (e === probe) continue;
        const s = getComputedStyle(e), r = e.getBoundingClientRect();
        if (s.display === 'none' || s.visibility === 'hidden' || !r.width || !r.height) continue;
        const text = FIELDS.has(e.tagName) || [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
        check(s, name(e), text, SHAPES.has(e.tagName.toLowerCase()) && e instanceof SVGElement);
        for (const pseudo of ['::before', '::after']) {
          const ps = getComputedStyle(e, pseudo);
          if (ps.content && ps.content !== 'none' && ps.content !== 'normal' && ps.display !== 'none') check(ps, name(e) + pseudo, /^["']./.test(ps.content), false);
        }
        if (text) {
          const f = fonts[s.fontFamily] ??= { n: 0, where: name(e), example: null };
          f.n++;
          // A light-DOM example lets DevTools ask which font Chrome actually rendered.
          if (!f.example && e.getRootNode() === document) { f.example = String(Object.keys(fonts).indexOf(s.fontFamily)); e.setAttribute('data-uiref-font', f.example); }
        }
      }
      probe.remove();
      return { colors, fonts, kitColors: kit.length };
    })()`);
    await c.send('DOM.enable');
    await c.send('CSS.enable');
    const { root } = await c.send('DOM.getDocument', { depth: 0 });
    for (const f of Object.values(page.fonts)) {
      if (f.example === null) continue;
      const { nodeId } = await c.send('DOM.querySelector', { nodeId: root.nodeId, selector: `[data-uiref-font="${f.example}"]` });
      if (!nodeId) continue;
      const { fonts } = await c.send('CSS.getPlatformFontsForNode', { nodeId });
      f.rendered = fonts.sort((a, b) => b.glyphCount - a.glyphCount)[0]?.familyName;
    }
    return page;
  });
  if (!found.kitColors) throw new Error('no colours found in the --from files');
  const offFonts = [];
  for (const [family, f] of Object.entries(found.fonts)) {
    const declared = family.split(',')[0].trim().replace(/^["']|["']$/g, '');
    if (GENERIC.has(declared.toLowerCase())) {
      if (!inKit(declared)) offFonts.push(`font "${declared}" (a system font) is not named in the kit: ${f.n} element(s), e.g. ${f.where}`);
    } else if (!inKit(declared)) offFonts.push(`font "${declared}" not in the kit: ${f.n} element(s), e.g. ${f.where}`);
    else if (f.rendered && !inKit(f.rendered) && !inKit(f.rendered.split(' ')[0]))
      offFonts.push(`font "${declared}" is declared but "${f.rendered}" renders (not loaded?): ${f.n} element(s), e.g. ${f.where}`);
  }
  const offColors = Object.entries(found.colors).sort((a, b) => b[1].n - a[1].n);
  for (const [c, v] of offColors) console.log(`colour ${c} not in the kit: ${v.n} use(s), e.g. ${v.where}`);
  for (const line of offFonts) console.log(line);
  const n = offColors.length + offFonts.length;
  console.log(n ? `${n} off-kit value(s)` : 'ok');
  process.exitCode = n ? 1 : 0;
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
    if (!opt.out) need(opt, 'app', 'flow');
    const { bytes, final } = await shoot(pos[0], opt);
    let note = opt.note || '';
    if (warnRedirect(pos[0], final)) {
      note = [note, `redirected to ${final}`].filter(Boolean).join('; ');
    }
    if (opt.out) {
      mkdirSync(dirname(resolve(opt.out)), { recursive: true });
      writeFileSync(resolve(opt.out), bytes);
      console.log(resolve(opt.out));
    } else {
      record(bytes, '.png', { app: opt.app, flow: opt.flow, platform: opt.phone ? 'web-phone' : 'web', source: pos[0],
        note: [opt.selector && `element ${opt.selector}`, opt.mono && 'grayscale', note].filter(Boolean).join('; ') });
    }
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
  } else if (cmd === 'mono' && pos.length) await mono(pos);
  else if (cmd === 'tokens' && pos[0]) await tokens(pos[0], opt);
  else if (cmd === 'search') {
    const words = pos.map(w => w.toLowerCase());
    for (const e of load().filter(e => words.every(w => [e.app, e.flow, e.platform, e.note, e.source].join(' ').toLowerCase().includes(w))))
      console.log(`${e.app} | ${e.flow} | ${e.platform} | ${e.captured} | ${e.file}`);
  } else if (cmd === 'gallery') gallery();
  else { console.error(readFileSync(new URL(import.meta.url), 'utf8').split('\n').filter(l => l.startsWith('//')).join('\n')); process.exitCode = 2; }
} catch (e) { console.error(`error: ${e.message}`); process.exitCode = 1; }
