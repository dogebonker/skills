#!/usr/bin/env node
// Check a references board before showing it: node check.mjs <board.html>
// Fails on missing or remote images, unknown regions or statuses, approved items a round left unjudged, and text over its word limit.
import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const path = process.argv[2];
if (!path) { console.error('usage: node check.mjs <board.html>'); process.exit(2); }
const html = readFileSync(path, 'utf8');
const m = html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/);
if (!m) { console.error('no <script id="data" type="application/json"> block'); process.exit(1); }
let D;
try { D = JSON.parse(m[1]); } catch (e) { console.error(`data block is not valid JSON: ${e.message}`); process.exit(1); }
if (!D || typeof D !== 'object' || Array.isArray(D)) { console.error('data block must be a JSON object'); process.exit(1); }
const list = k => (Array.isArray(D[k]) ? D[k] : []);

const problems = [];
const words = s => String(s ?? '').split(/\s+/).filter(Boolean).length;
const limit = (where, s, n) => { if (words(s) > n) problems.push(`${where}: ${words(s)} words, limit ${n}`); };
const image = (where, src) => {
  if (!src) return problems.push(`${where}: missing image`);
  if (typeof src !== 'string') return problems.push(`${where}: image path must be a string`);
  if (src.startsWith('data:')) return;
  if (/^https?:/.test(src)) return problems.push(`${where}: remote image; save it with library.mjs so the board stays local`);
  if (!existsSync(resolve(dirname(path), src))) problems.push(`${where}: image not found: ${src}`);
};
const shot = (where, s) => { if (!s || typeof s !== 'object') return problems.push(`${where}: missing`); image(`${where}.src`, s.src); image(`${where}.mono`, s.mono); };

for (const k of ['title', 'goal', 'target', 'kit', 'regions', 'spec']) if (!D[k]) problems.push(`missing ${k}`);
for (const k of ['kit', 'regions', 'spec', 'rounds', 'taste']) if (D[k] !== undefined && !Array.isArray(D[k])) problems.push(`${k} must be a list`);
if (!list('kit').length) problems.push('kit lists the design kit files the tokens check reads');
const isObj = v => v && typeof v === 'object' && !Array.isArray(v);
const regions = new Map();
list('regions').forEach((g, i) => {
  if (!isObj(g)) return problems.push(`regions[${i}] must be an object`);
  const at = `region ${g.id}`;
  if (regions.has(g.id)) problems.push(`${at}: duplicate id`);
  regions.set(g.id, g);
  const refs = Array.isArray(g.refs) ? g.refs : [];
  if (!refs.length) problems.push(`${at}: needs at least one reference`);
  refs.forEach((r, j) => shot(`${at}.refs[${j}]`, r));
  if (g.picked && !refs.some(r => r?.app === g.picked)) problems.push(`${at}: picked "${g.picked}" is not one of its refs`);
  shot(`${at}.ours`, g.ours);
});
const ids = new Set();
list('spec').forEach((t, i) => {
  if (!isObj(t)) return problems.push(`spec[${i}] must be an object`);
  const at = `spec ${t.id}`;
  if (ids.has(t.id)) problems.push(`${at}: duplicate id`);
  ids.add(t.id);
  if (!regions.has(t.region)) problems.push(`${at}: unknown region ${t.region}`);
  if (!['proposed', 'approved', 'rejected'].includes(t.status)) problems.push(`${at}: status must be proposed, approved or rejected`);
  if (t.status === 'rejected' && !t.reason) problems.push(`${at}: a rejected item records the user's reason`);
  limit(`${at}.item`, t.item, 20);
});
const approved = list('spec').filter(t => isObj(t) && t.status === 'approved');
if (list('rounds').length && list('spec').some(t => t?.status === 'proposed')) problems.push('rounds exist while spec items are still proposed: approve or reject them first');
list('rounds').forEach((r, i) => {
  if (!isObj(r)) return problems.push(`rounds[${i}] must be an object`);
  const at = `round ${r.n ?? i + 1}`;
  for (const id of regions.keys()) shot(`${at}.shots.${id}`, r.shots?.[id]);
  for (const t of approved) {
    const res = r.results?.[t.id];
    if (typeof res?.pass !== 'boolean') problems.push(`${at}: ${t.id} has no pass/fail`);
    else limit(`${at}.results.${t.id}.why`, res.why, 15);
  }
  for (const id of Object.keys(isObj(r.results) ? r.results : {})) if (!approved.some(t => t.id === id)) problems.push(`${at}: result for ${id}, which is not an approved item`);
  if (!Number.isInteger(r.offKit) || r.offKit < 0) problems.push(`${at}: offKit is the tokens check's off-kit count`);
});
console.log(problems.join('\n') || 'ok');
process.exit(problems.length ? 1 : 0);
