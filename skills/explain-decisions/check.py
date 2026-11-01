#!/usr/bin/env python3
"""Check a decisions page before showing it: python3 check.py page.html

Fails on missing fields, bad references and text over its word limit.
Exits 1 and lists every problem, or prints "ok".
"""
import json
import os
import re
import sys

LIMITS = {
    'goal': 25, 'problem': 25, 'ask': 15, 'whyNow': 15, 'ifSilent': 15, 'plain': 30, 'name': 6, 'result': 15,
    't': 5, 'd': 25, 'text': 15, 'q': 20, 'explain': 25, 'why': 25, 'drawback': 15,
    'caveat': 40, 'message': 50, 'safeDefault': 20, 'note': 25, 'alt': 30,
}
AREAS = ('code', 'data', 'people', 'users', 'undo', 'cost')
VIEW_LABELS = ('Current — observed', 'Current — not verified', 'Proposed', 'Illustrative')


def words(s):
    return len(str(s).split())


def check_limits(node, path, problems):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and k in LIMITS and words(v) > LIMITS[k]:
                problems.append(f'{path}.{k}: {words(v)} words, limit {LIMITS[k]}')
            check_limits(v, f'{path}.{k}', problems)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            check_limits(v, f'{path}[{i}]', problems)


def check(data, base=None):
    p = []
    for k in ('title', 'problem', 'goal', 'questions'):
        if not data.get(k):
            p.append(f'missing {k}')
    ov = data.get('overview') or {}
    if not ov.get('src') or not ov.get('alt'):
        p.append('overview needs src and alt (the zoomed-out picture)')
    elif base and not os.path.isfile(os.path.join(base, ov['src'])):
        p.append(f'overview: {ov["src"]} not found next to the page')
    for term, d in (data.get('terms') or {}).items():
        if words(d) > 15:
            p.append(f'terms.{term}: {words(d)} words, limit 15')
    check_limits({k: v for k, v in data.items() if k != 'terms'}, 'page', p)
    for n, q in enumerate(data.get('questions') or [], 1):
        at = f'q{n}'
        for k in ('ask', 'whyNow', 'ifSilent', 'plain', 'views', 'options', 'quiz', 'pick', 'owner'):
            if not q.get(k):
                p.append(f'{at}: missing {k}')
        for i, v in enumerate(q.get('views') or []):
            if v.get('label') not in VIEW_LABELS:
                p.append(f'{at}.views[{i}]: label must be one of {VIEW_LABELS}')
            if v.get('label') == 'Current — observed' and not v.get('ref'):
                p.append(f'{at}.views[{i}]: "Current — observed" needs a ref (file:line)')
            if len(v.get('flow') or []) < 2:
                p.append(f'{at}.views[{i}]: flow needs at least 2 steps')
            if not v.get('result'):
                p.append(f'{at}.views[{i}]: missing result')
        opts = q.get('options') or []
        if len(opts) < 2:
            p.append(f'{at}: needs at least 2 options')
        for o in opts:
            r = o.get('radius') or {}
            for a in AREAS:
                lvl = (r.get(a) or {}).get('level')
                if lvl not in (0, 1, 2, 3) or not (r.get(a) or {}).get('text'):
                    p.append(f'{at}.option {o.get("key")}: radius.{a} needs level 0-3 and text')
        keys = {o.get('key') for o in opts}
        if (q.get('pick') or {}).get('key') not in keys:
            p.append(f'{at}: pick.key must be one of {sorted(map(str, keys))}')
        if (q.get('pick') or {}).get('sure') not in ('said', 'line', 'ran'):
            p.append(f'{at}: pick.sure must be said, line or ran')
        for i, z in enumerate(q.get('quiz') or []):
            if not isinstance(z.get('answer'), int) or not 0 <= z['answer'] < len(z.get('choices') or []):
                p.append(f'{at}.quiz[{i}]: answer must index into choices')
        ans = q.get('answer')
        if ans is not None and (ans.get('key') not in keys or not ans.get('by') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(ans.get('date')))):
            p.append(f'{at}: answer needs key (an option), by, and date as YYYY-MM-DD')
        if not (q.get('owner') or {}).get('who'):
            p.append(f'{at}: owner.who is required (use "You" when the call is yours)')
        pics = q.get('pictures') or []
        if not pics:
            kind = 'a frame-by-frame storyboard' if q.get('ui') else 'a strip'
            p.append(f'{at}: needs pictures[] ({kind} PNG)')
        for i, pic in enumerate(pics):
            src = pic.get('src') or ''
            if not src or not pic.get('alt'):
                p.append(f'{at}.pictures[{i}]: needs src and alt')
            elif base and not os.path.isfile(os.path.join(base, src)):
                p.append(f'{at}.pictures[{i}]: {src} not found next to the page')
    return p


def load(path):
    html = open(path, encoding='utf-8').read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        sys.exit(f'{path}: no <script id="data" type="application/json"> block')
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit(f'{path}: data block is not valid JSON: {e}')


def main(path):
    problems = check(load(path), os.path.dirname(os.path.abspath(path)))
    print('\n'.join(problems) or 'ok')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main(sys.argv[1])
