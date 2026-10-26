#!/usr/bin/env python3
"""Build the decision log for one feature folder: python3 index.py <folder>

Writes <folder>/index.html listing every question from every page, in file order,
with what was decided, by whom, and any open caveat.
"""
import html
import pathlib
import sys

from check import load

STYLE = """
:root { --bg: #f7f7f5; --panel: #fff; --ink: #1a1a19; --muted: #6b6a66; --line: #e6e5e1; --ok: #1f8a4c; --open: #b35c00; --warn: #fbe3c7; }
@media (prefers-color-scheme: dark) { :root { --bg: #121211; --panel: #1b1b1a; --ink: #f2f1ee; --muted: #a09f9a; --line: #2c2c2a; --ok: #4fd18b; --open: #ffb15c; --warn: #7a4110; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 system-ui, -apple-system, sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 24px 16px 48px; overflow-wrap: anywhere; }
h1 { font-size: 1.35rem; margin: 0; } .sub { color: var(--muted); margin: 4px 0 20px; }
ol { list-style: none; padding: 0; margin: 0; border-left: 2px solid var(--line); }
li { position: relative; margin: 0 0 14px 18px; background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }
li::before { content: ""; position: absolute; left: -26px; top: 18px; width: 12px; height: 12px; border-radius: 50%; background: var(--open); }
li.done::before { background: var(--ok); }
a { color: inherit; } h2 { font-size: 1.05rem; margin: 0; } p { margin: 6px 0 0; }
.plain { color: var(--muted); } .status { font-weight: 600; } .done .status { color: var(--ok); } li:not(.done) .status { color: var(--open); }
.caveat { background: var(--warn); border-radius: 8px; padding: 6px 10px; font-size: 14px; }
"""


def row(page, n, q):
    e = html.escape
    opts = {o['key']: o['name'] for o in q['options']}
    ans, pick = q.get('answer'), q['pick']
    if ans:
        status = f"Decided {e(ans['key'])} · {e(opts[ans['key']])}, by {e(ans['by'])} on {e(ans['date'])}"
        if ans['key'] != pick['key']:
            status += f" (overrode pick {e(pick['key'])})"
    else:
        status = f"Open. My pick: {e(pick['key'])} · {e(opts[pick['key']])}"
    caveat = f'<p class="caveat"><b>Still unproven:</b> {e(pick["caveat"])}</p>' if pick.get('caveat') else ''
    return (f'<li class="{"done" if ans else ""}"><h2><a href="{e(page.name)}#q{n}">{e(q["ask"])}</a></h2>'
            f'<p class="plain">{e(q["plain"])}</p><p class="status">{status}</p>{caveat}</li>')


def main(folder):
    folder = pathlib.Path(folder)
    pages = sorted(p for p in folder.glob('*.html') if p.name != 'index.html')
    rows, total, done = [], 0, 0
    for page in pages:
        for n, q in enumerate(load(page)['questions'], 1):
            rows.append(row(page, n, q))
            total += 1
            done += bool(q.get('answer'))
    title = html.escape(folder.name)
    (folder / 'index.html').write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} decisions</title>'
        f'<style>{STYLE}</style></head><body><main><h1>{title}: decision log</h1>'
        f'<p class="sub">{done} of {total} decided. Each entry opens its full explanation.</p>'
        f'<ol>{"".join(rows)}</ol></main></body></html>\n', encoding='utf-8')
    print(f'{folder / "index.html"}: {done}/{total} decided')


if __name__ == '__main__':
    main(sys.argv[1])
