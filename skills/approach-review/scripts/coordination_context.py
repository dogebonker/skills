#!/usr/bin/env python3
"""Read-only, heuristic SQL coordination navigation evidence for the current directory."""
import json
import re
import sys
from pathlib import Path

IGNORED = {'.git', 'node_modules', 'vendor', 'venv', '.venv', '__pycache__', '.cache', 'cache', '.pytest_cache'}
IDENT = r'"?[A-Za-z_][\w$]*"?(?:\."?[A-Za-z_][\w$]*"?)*'
LOCK = re.compile(r'\bFOR\s+(?:NO\s+KEY\s+UPDATE|KEY\s+SHARE|UPDATE|SHARE)\b', re.I)


def clean(sql):
    return re.sub(r'/\*.*?\*/|--[^\n]*', lambda m: re.sub(r'[^\n]', ' ', m[0]), sql, flags=re.S)


def table_name(value):
    return value.replace('"', '').lower()


def collect(root):
    root = root.resolve()
    notes = []
    source, diff_paths = root, []
    if (root / 'source').is_dir() and not (root / 'source').is_symlink() and (root / 'change.diff').is_file():
        source, diff_paths = root / 'source', [root / 'change.diff']
    else:
        packets = sorted(p for p in root.glob('*.diff') if p.with_suffix('').is_dir())
        if packets:
            diff_paths = packets
            notes.append('Sibling directory/diff packets discovered; paths retain packet prefixes.')
    files, diffs, total = {}, {}, 0
    # Resolve each candidate against cwd; directory symlinks are never traversed.
    def walk(directory):
        try:
            children = sorted(directory.iterdir())
        except OSError:
            notes.append('Unreadable directory: ' + str(directory.relative_to(root)))
            return
        for path in children:
            if path.name in IGNORED or path.is_symlink():
                continue
            if path.is_dir():
                yield from walk(path)
            elif path.suffix in {'.sql', '.go', '.diff'}:
                yield path
    for path in walk(source):
        if len(files) + len(diffs) >= 6000 or total >= 60_000_000:
            notes.append('Source scan truncated at 6000 files or 60 MB.')
            break
        try:
            if not path.resolve().is_relative_to(root) or path.stat().st_size > 2_000_000:
                notes.append('Skipped oversized or escaping file: ' + str(path.relative_to(root)))
                continue
            value = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            notes.append('Unreadable/non-UTF8 file: ' + str(path.relative_to(root)))
            continue
        total += len(value.encode())
        if path.suffix == '.diff':
            diffs[path] = value
        else:
            files[str(path.relative_to(root))] = value
    for path in diff_paths:
        if path not in diffs and not path.is_symlink() and path.resolve().is_relative_to(root):
            try:
                if path.stat().st_size <= 2_000_000:
                    diffs[path] = path.read_text(encoding='utf-8')
                else:
                    notes.append('Provided diff exceeds 2 MB; skipped.')
            except (OSError, UnicodeError):
                notes.append('Provided diff could not be read.')
    changed, methods = {}, set()
    for path, diff in sorted(diffs.items()):
        if diff_paths and path not in diff_paths:
            continue
        prefix = str(source.relative_to(root)) if source != root else ''
        if path in diff_paths and path.name != 'change.diff':
            prefix = path.stem
        current, line = '', 0
        for text in diff.splitlines():
            if text.startswith('+++ '):
                current = text[4:].removeprefix('b/').split('\t')[0]
                current = '/'.join(p for p in (prefix, current) if p)
            elif text.startswith('@@ '):
                match = re.search(r'\+(\d+)', text)
                line = int(match[1]) if match else 0
            elif text[:1] in {'+', ' '}:
                if text.startswith('+'):
                    changed.setdefault(current, set()).add(line)
                if current.endswith('.go'):
                    methods.update(re.findall(r'\.([A-Za-z_]\w*)\s*\(', text[1:]))
                line += 1
    def evidence(path, start, end):
        lines = files[path].splitlines()
        end = min(end, len(lines))
        stop = min(end, start + 69)
        return {'file': path, 'line': start, 'end_line': stop,
                'snippet': '\n'.join(lines[start - 1:stop])[:6500],
                'truncated': end > stop or len('\n'.join(lines[start - 1:stop])) > 6500}
    queries, edges = [], []
    for path, original in sorted(files.items()):
        if not path.endswith('.sql'):
            continue
        down = re.search(r'^\s*--\s*\+goose\s+Down\b', original, re.M | re.I)
        sql = original[:down.start()] if down else original
        headers = list(re.finditer(r'^[ \t]*--\s*name:\s*(\w+)\s*:', sql, re.M))
        for i, header in enumerate(headers):
            end = headers[i + 1].start() if i + 1 < len(headers) else len(sql)
            body = clean(sql[header.end():end])
            start_line = sql.count('\n', 0, header.start()) + 1
            end_line = len(sql[:end].splitlines())
            tables = []
            for match in re.finditer(r'\b(?:FROM|JOIN|UPDATE|INTO)\s+(' + IDENT + r')(?:\s+(?:AS\s+)?(\w+))?', LOCK.sub('', body), re.I):
                tables.append({'table': table_name(match[1]), 'alias': match[2] if match[2] and match[2].upper() not in {'WHERE', 'SET', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'ON', 'FOR', 'ORDER', 'LIMIT', 'RETURNING'} else None})
            locks = [m[0] for m in LOCK.finditer(body)]
            of = re.search(r'\bFOR\s+(?:NO\s+KEY\s+UPDATE|KEY\s+SHARE|UPDATE|SHARE)\s+OF\s+([\w", .]+)', body, re.I)
            locked = {t['table'] for t in tables}
            if of:
                aliases = {v.strip().strip('"') for v in re.split(r'\bNOWAIT\b|\bSKIP\b', of[1], flags=re.I)[0].split(',')}
                locked = {t['table'] for t in tables if t['alias'] in aliases or t['table'] in aliases}
            deleted = re.findall(r'\bDELETE\s+FROM\s+(' + IDENT + ')', body, re.I)
            queries.append({'name': header[1], 'tables': tables, 'lock_modes': locks,
                            'locked_tables': sorted(locked) if locks else [],
                            'deletes': [table_name(t) for t in deleted],
                            'touched_or_referenced': header[1] in methods or bool(changed.get(path, set()) & set(range(start_line, end_line + 1))),
                            **evidence(path, start_line, end_line)})
        # shortcut: historical DDL is heuristic; use an effective-schema parser when migration replay is required.
        masked = clean(sql)
        for statement in re.finditer(r'[^;]+(?:;|$)', masked):
            heads = list(re.finditer(r'\b(?:CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?|ALTER\s+TABLE\s+(?:ONLY\s+)?)(' + IDENT + ')', statement[0], re.I))
            for j, head in enumerate(heads):
                segment = statement[0][head.end():heads[j + 1].start() if j + 1 < len(heads) else len(statement[0])]
                for ref in re.finditer(r'\bREFERENCES\s+(' + IDENT + r')\s*(?:\([^)]*\))?([^,;]*)', segment, re.I):
                    offset = statement.start() + head.end() + ref.start()
                    line = masked.count('\n', 0, offset) + 1
                    action = re.search(r'\bON\s+DELETE\s+(CASCADE|SET\s+NULL|SET\s+DEFAULT|RESTRICT|NO\s+ACTION)', ref[2], re.I)
                    edges.append({'child': table_name(head[1]), 'parent': table_name(ref[1]),
                                  'on_delete': re.sub(r'\s+', ' ', action[1].upper()) if action else 'unspecified',
                                  'schema_status': 'historical DDL evidence; may be superseded',
                                  **evidence(path, max(1, line - 2), min(line + 2, len(sql.splitlines())))})
    provided = bool(diffs)
    selected = [q for q in queries if q['lock_modes'] and (q['touched_or_referenced'] or not provided)]
    tables = {t for q in selected for t in q['locked_tables']}
    ancestors = set(tables)
    while True:
        expanded = ancestors | {e['parent'] for e in edges if e['child'] in ancestors and e['on_delete'] == 'CASCADE'}
        if expanded == ancestors:
            break
        ancestors = expanded
    relevant_edges = sorted((e for e in edges if e['child'] in ancestors), key=lambda e: e['on_delete'] != 'CASCADE')
    deletes = sorted((q for q in queries if set(q['deletes']) & ancestors), key=lambda q: not bool(set(q['deletes']) & (ancestors - tables)))
    names = {q['name'] for q in selected + deletes}
    callers = []
    pattern = re.compile(r'\.(' + '|'.join(re.escape(n) for n in sorted(names)) + r')\s*\(') if names else None
    for path, value in sorted(files.items()):
        if not pattern or not path.endswith('.go') or path.endswith('.sql.go'):
            continue
        for match in pattern.finditer(value):
            line = value.count('\n', 0, match.start()) + 1
            callers.append({'query': match[1], 'call_line': line, **evidence(path, max(1, line - 8), line + 8)})
    ancestor_deletes = {q['name'] for q in deletes if set(q['deletes']) & (ancestors - tables)}
    callers.sort(key=lambda c: (c['query'] not in ancestor_deletes, c['file'].endswith('_test.go')))
    result = {'purpose': 'Navigation evidence only; no bug verdict or proof of locking/reachability.',
              'review_cautions': ['Verify effective schema: historical migrations may conflict or be superseded.',
                                  'Verify conflicting lock modes, locked aliases, transaction order and reachable callers.',
                                  'Heuristic regex extraction is not a SQL/Go parser; dynamic SQL and unnamed queries may be missed.'],
              'diff_present': provided, 'locked_tables': sorted(tables), 'cascade_ancestor_tables': sorted(ancestors - tables),
              'notes': notes, 'counts_before_truncation': {}}
    for key, items, limit in [('touched_lock_queries', selected, 24), ('fk_evidence', relevant_edges, 80),
                              ('related_delete_queries', deletes, 35), ('go_callers', callers, 65)]:
        result['counts_before_truncation'][key] = len(items)
        result[key] = items[:limit]
        if len(items) > limit:
            notes.append(f'{key} truncated: showing {limit} of {len(items)} records.')
    note_count = len(notes)
    result['notes'] = [note[:180] + (' [truncated]' if len(note) > 180 else '') for note in notes[:10]]
    if note_count > 10:
        result['notes'].append(f'{note_count - 10} additional scan/truncation notes omitted.')
    priorities = ('touched_lock_queries', 'related_delete_queries', 'fk_evidence', 'go_callers')
    counts = result['counts_before_truncation']
    for key in ('locked_tables', 'cascade_ancestor_tables'):
        counts[key] = len(result[key])
    result['omitted_counts'] = {key: counts[key] - len(result[key]) for key in counts}
    if len(encode(result).encode()) > 27_999:
        result['notes'].append('28 KB output budget applied; inspect omitted_counts and navigate source for remaining evidence.')
        for key in reversed(('locked_tables', 'cascade_ancestor_tables') + priorities):
            while result[key] and len(encode(result).encode()) > 27_999:
                result[key].pop()
                result['omitted_counts'][key] = counts[key] - len(result[key])
    return result


def encode(result):
    return json.dumps(result, ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    if len(sys.argv) != 1:
        sys.exit('Usage: coordination_context.py (no arguments; reads current directory)')
    print(encode(collect(Path.cwd().resolve())))
