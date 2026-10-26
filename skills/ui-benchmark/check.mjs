#!/usr/bin/env node
// Check a benchmark board before showing it: node check.mjs <board.html>
// Fails on bad scores, pins off the screen, missing images, unknown fit values and notes over their word limit.
import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const path = process.argv[2];
if (!path) { console.error('usage: node check.mjs <board.html>'); process.exit(2); }
const html = readFileSync(path, 'utf8');
const m = html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/);
if (!m) { console.error('no <script id="data" type="application/json"> block'); process.exit(1); }
let D;
try { D = JSON.parse(m[1]); } catch (e) { console.error(`data block is not valid JSON: ${e.message}`); process.exit(1); }

const problems = [];
const words = s => String(s ?? '').split(/\s+/).filter(Boolean).length;
const limit = (where, s, n) => { if (words(s) > n) problems.push(`${where}: ${words(s)} words, limit ${n}`); };
const image = (where, src) => {
  if (!src) return problems.push(`${where}: missing image`);
  if (src.startsWith('data:')) return;
  if (/^https?:/.test(src)) return problems.push(`${where}: remote image; save it to the library with add, so the board stays local`);
  if (!existsSync(resolve(dirname(path), src))) problems.push(`${where}: image not found: ${src}`);
};
const scores = (where, s) => {
  if (!Array.isArray(s) || s.length !== 10 || s.some(v => v !== null && !(Number.isInteger(v) && v >= 0 && v <= 4)))
    problems.push(`${where}: needs 10 heuristic scores, each 0-4 or null for n/a`);
};
const pins = (where, list = []) => list.forEach((p, i) => {
  if (!(typeof p.x === 'number' && typeof p.y === 'number' && p.x >= 0 && p.x <= 100 && p.y >= 0 && p.y <= 100)) problems.push(`${where}.pins[${i}]: x and y are percentages, 0-100`);
  if (!['good', 'bad'].includes(p.kind)) problems.push(`${where}.pins[${i}]: kind must be good or bad`);
  limit(`${where}.pins[${i}].note`, p.note, 15);
});

for (const k of ['title', 'feature', 'flow', 'apps']) if (!D[k]) problems.push(`missing ${k}`);
const apps = D.apps || [];
if (apps.filter(a => a.target).length !== 1) problems.push('exactly one app needs "target": true');
if (apps.length < 3) problems.push('compare the target with at least 2 reference apps');
apps.forEach(a => {
  const at = `app "${a.name}"`;
  limit(`${at}.verdict`, a.verdict, 20);
  scores(`${at}.scores`, a.scores);
  if (!a.screens?.length) problems.push(`${at}: needs at least one screen`);
  (a.screens || []).forEach((s, i) => { image(`${at}.screens[${i}]`, s.src); pins(`${at}.screens[${i}]`, s.pins); });
  for (const [k, v] of Object.entries(a.visual || {})) limit(`${at}.visual.${k}`, v, 15);
});
(D.borrow || []).forEach((b, i) => {
  if (!['fits', 'change', 'conflicts'].includes(b.fit)) problems.push(`borrow[${i}]: fit must be fits, change or conflicts`);
  if (b.fit !== 'fits' && !b.designRef) problems.push(`borrow[${i}]: say which DESIGN.md or PRODUCT.md rule it needs or breaks`);
  limit(`borrow[${i}].idea`, b.idea, 12);
});
if (D.compare) {
  image('compare.before', D.compare.before);
  image('compare.after', D.compare.after);
  if (D.compare.reference) image('compare.reference', D.compare.reference);
  pins('compare', D.compare.pins);
  if (D.compare.scoresAfter) scores('compare.scoresAfter', D.compare.scoresAfter);
}
console.log(problems.join('\n') || 'ok');
process.exit(problems.length ? 1 : 0);
