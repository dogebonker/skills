#!/usr/bin/env python3
"""Inventory test units (TS/JS, Python, Rust, Go) into inventory.jsonl.

Usage: inventory.py <repo> [--paths glob...] [-o inventory.jsonl]
"""
import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import astgrep  # noqa: E402

TS_LANGS = {".ts": "TypeScript", ".mts": "TypeScript", ".cts": "TypeScript", ".tsx": "Tsx",
            ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript"}
ALWAYS_SKIP = {"node_modules", "vendor", ".git"}
WALK_SKIP = ALWAYS_SKIP | {"target", "dist", "build", ".venv", "venv", "__pycache__", ".next", ".turbo"}
RS_TEST_ATTR = re.compile(r"#\[\s*(?:\w+\s*::\s*)*(?:\w*test|rstest)\b")
GO_TEST_FUNC = re.compile(r"func\s+Test(?![a-z])\w*\s*\(\s*\w+\s+\*testing\.T\s*\)")
# Members that make `it.x(...)` / `test.x(...)` a hook or helper, not a test definition.
TS_NOT_TESTS = {"beforeEach", "afterEach", "beforeAll", "afterAll", "use", "step", "extend",
                "setTimeout", "slow", "info", "expect", "flakyTest", "addSnapshotSerializer"}
TS_FUNC_ARG = re.compile(r"(async\b\s*)?(function\b|\([^)]*\)\s*(:[^=]*)?=>|[\w$]+\s*=>)")

TS_RULES = """id: ts-unit
language: {lang}
rule:
  kind: expression_statement
  inside: {{any: [{{kind: program}}, {{kind: statement_block}}]}}
  has: {{pattern: $F($$$ARGS)}}
constraints:
  F: {{regex: '^(it|test|describe|suite|layer)\\b'}}
"""
OTHER_RULES = """id: py-fn
language: Python
rule:
  any:
    - kind: decorated_definition
      has: {field: definition, kind: function_definition, has: {field: name, pattern: $NAME}}
    - kind: function_definition
      has: {field: name, pattern: $NAME}
      not: {inside: {kind: decorated_definition}}
  inside: {any: [{kind: module}, {kind: block, inside: {kind: class_definition}}]}
constraints:
  NAME: {regex: '^test'}
---
id: py-class
language: Python
rule:
  any:
    - kind: decorated_definition
      has: {field: definition, kind: class_definition, all: [{has: {field: name, pattern: $NAME}}, {has: {field: body, pattern: $BODY}}]}
    - kind: class_definition
      all: [{has: {field: name, pattern: $NAME}}, {has: {field: body, pattern: $BODY}}]
      not: {inside: {kind: decorated_definition}}
---
id: rs-fn
language: Rust
rule:
  kind: function_item
  has: {field: name, pattern: $NAME}
  inside: {any: [{kind: source_file}, {kind: declaration_list, inside: {kind: mod_item}}]}
---
id: rs-mod
language: Rust
rule: {kind: mod_item, has: {field: name, pattern: $NAME}}
---
id: rs-attr
language: Rust
rule: {any: [{kind: attribute_item}, {kind: line_comment}, {kind: block_comment}]}
---
id: go-fn
language: Go
rule: {kind: function_declaration, has: {field: name, pattern: $NAME}}
constraints:
  NAME: {regex: '^Test'}
---
id: go-run
language: Go
rule:
  kind: expression_statement
  has:
    kind: call_expression
    all:
      - has: {field: function, kind: selector_expression, has: {field: field, regex: '^Run$'}}
      - has: {field: arguments, has: {nthChild: 1, any: [{kind: interpreted_string_literal}, {kind: raw_string_literal}], pattern: $NAME}}
      - has: {field: arguments, has: {nthChild: 2, kind: func_literal}}
---
id: go-attr
language: Go
rule: {kind: comment}
"""
ERR_RULE = "id: err\nlanguage: {lang}\nrule: {{kind: ERROR}}\n"
ALL_LANGS = ("TypeScript", "Tsx", "JavaScript", "Python", "Rust", "Go")
RULES = "---\n".join([TS_RULES.format(lang=l) for l in ("TypeScript", "Tsx", "JavaScript")]
                     + [OTHER_RULES] + [ERR_RULE.format(lang=l) for l in ALL_LANGS])


def lang_of(rel):
    parts = rel.split("/")
    name, ext = parts[-1], os.path.splitext(parts[-1])[1]
    if ext in TS_LANGS and not name.endswith(".d.ts"):
        if re.search(r"\.(test|spec)\.", name) or "__tests__" in parts[:-1]:
            return "ts"
    elif ext == ".py":
        if name.startswith("test_") or name.endswith("_test.py") or "tests" in parts[:-1]:
            return "py"
    elif name.endswith("_test.go"):
        return "go"
    elif ext == ".rs":
        return "rs"  # confirmed by content in find_files
    return None


def list_files(repo):
    try:
        out = subprocess.run(["git", "-C", repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             capture_output=True, check=True).stdout.decode("utf-8", "replace")
        files = [f for f in out.split("\0") if f and os.path.isfile(os.path.join(repo, f))]
        skip = ALWAYS_SKIP
    except (OSError, subprocess.CalledProcessError):
        files, skip = [], WALK_SKIP
        for root, dirs, names in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in WALK_SKIP]
            files += [os.path.relpath(os.path.join(root, n), repo).replace(os.sep, "/") for n in names]
    return sorted(f for f in files if not skip & set(f.split("/")[:-1]))


def find_files(repo, globs=None):
    """Return {relative path: lang} for test files under repo."""
    found = {}
    for rel in list_files(repo):
        if globs and not any(fnmatch.fnmatch(rel, g) for g in globs):
            continue
        lang = lang_of(rel)
        if lang == "rs":
            with open(os.path.join(repo, rel), "rb") as f:
                if not RS_TEST_ATTR.search(f.read().decode("utf-8", "replace")):
                    continue
        if lang:
            found[rel] = lang
    return found


def py_compiles(data, name):
    try:
        compile(data, name, "exec", dont_inherit=True)
        return True
    except (SyntaxError, ValueError):
        return False


def _ts_title(text):
    if text[:1] in ("'", '"', "`") and len(text) >= 2:
        return text[1:-1], True
    return text, False


def _extend_back(data, start, pieces):
    """Grow `start` over attributes and doc comments directly above it (Rust, Go)."""
    while True:
        j = start
        while j > 0 and data[j - 1] in b" \t\r\n":
            j -= 1
        piece = pieces.get(j)
        if not piece:
            return start
        ps, is_attr = piece
        if not is_attr and data.count(b"\n", j, start) > 1:  # a blank line detaches a comment
            return start
        start = ps


def _parse_file(lang, data, matches):
    """Return (units, containers) for one file as dicts with start/end byte offsets and title."""
    units, containers = [], []
    if lang == "ts":
        for m in matches:
            mv = m["metaVariables"]
            f = mv["single"]["F"]["text"]
            args = [a["text"] for a in mv["multi"].get("ARGS", []) if a["text"] != "," and not a["text"].startswith(("//", "/*"))]
            chain = re.match(r"(\w+)((?:\s*\.\s*\w+)*)", f)
            root, members = chain.group(1), re.findall(r"\w+", chain.group(2))
            curried = len(f) > chain.end()  # it.each(table)(...), it.layer(L)(...)
            if TS_NOT_TESTS & set(members) or not args:
                continue
            is_container = root in ("describe", "suite") or "describe" in members or (curried and (root == "layer" or "layer" in members))
            if root == "layer" and not is_container:
                continue
            s, e = m["range"]["byteOffset"]["start"], m["range"]["byteOffset"]["end"]
            if TS_FUNC_ARG.match(args[0]):
                if is_container:  # effect `layer(L)((it) => ...)`: a container with no name
                    containers.append({"start": s, "end": e, "title": None, "kind": "describe"})
                continue
            title, literal = _ts_title(args[0])
            if not literal and not any(TS_FUNC_ARG.match(a) for a in args[1:]):
                continue
            (containers if is_container else units).append({"start": s, "end": e, "title": title, "kind": "describe"})
    elif lang == "py":
        for m in matches:
            s, e = m["range"]["byteOffset"]["start"], m["range"]["byteOffset"]["end"]
            mv = m["metaVariables"]["single"]
            if m["ruleId"] == "py-fn":
                decorators = data[s:mv["NAME"]["range"]["byteOffset"]["start"]]
                if not re.search(rb"@\s*[\w.]*fixture\b", decorators):  # `@pytest.fixture def test_client()`
                    units.append({"start": s, "end": e, "title": mv["NAME"]["text"]})
            else:
                body = mv["BODY"]["range"]["byteOffset"]
                header = data[mv["NAME"]["range"]["byteOffset"]["end"]:body["start"]].decode("utf-8", "replace")
                bases = re.findall(r"[\w.]+(?:\s*=\s*[\w.]+)?", header)
                name = mv["NAME"]["text"]
                containers.append({"start": s, "end": e, "title": name, "kind": "class", "bases": bases,
                                   "body_start": body["start"],
                                   "is_test_class": name.startswith("Test") or any(b.endswith("TestCase") for b in bases)})
        # A test method counts only when its innermost class is a test class.
        kept = []
        for u in units:
            enclosing = [c for c in containers if c["start"] < u["start"] and u["end"] <= c["end"]]
            if not enclosing or max(enclosing, key=lambda c: c["start"])["is_test_class"]:
                kept.append(u)
        units = kept
    else:
        pieces = {}
        for m in matches:
            if m["ruleId"] in ("rs-attr", "go-attr"):
                s = m["range"]["byteOffset"]["start"]
                text = data[s:m["range"]["byteOffset"]["end"]].rstrip()
                is_attr = text.startswith(b"#[")
                own_line = not data[data.rfind(b"\n", 0, s) + 1:s].strip()
                if own_line and (is_attr or lang == "go" or re.match(rb"///(?!/)|/\*\*(?!\*)", text)):
                    pieces[s + len(text)] = (s, is_attr)
        for m in matches:
            rid = m["ruleId"]
            if rid in ("rs-attr", "go-attr"):
                continue
            s, e = m["range"]["byteOffset"]["start"], m["range"]["byteOffset"]["end"]
            name = m["metaVariables"]["single"]["NAME"]["text"]
            if rid == "go-run":
                units.append({"start": s, "end": e, "title": name[1:-1], "run": True})
                continue
            xs = _extend_back(data, s, pieces)
            head = data[xs:s].decode("utf-8", "replace")
            if rid == "rs-mod":
                containers.append({"start": xs, "end": e, "title": name, "kind": "mod"})
            elif rid == "rs-fn" and RS_TEST_ATTR.search(re.sub(r"//[^\n]*|/\*.*?\*/", "", head, flags=re.S)):
                units.append({"start": xs, "end": e, "title": name})
            elif rid == "go-fn" and GO_TEST_FUNC.match(data[s:e].decode("utf-8", "replace")):
                units.append({"start": xs, "end": e, "title": name})
        if lang == "go":  # subtests count only inside a TestXxx function
            tops = [u for u in units if not u.get("run")]
            units = tops + [u for u in units if u.get("run") and any(t["start"] < u["start"] and u["end"] <= t["end"] for t in tops)]
            # A function or t.Run with literal-named subtests is a container, like a describe, so it is never
            # judged (or kept) apart from them. Seen on a Go repo: a kept parent "covered" its deleted subtests and
            # was left with setup only. Apply keeps an emptied parent that still has code of its own.
            parents = [u for u in units if any(v is not u and u["start"] <= v["start"] and v["end"] <= u["end"] for v in units)]
            containers += [{"start": u["start"], "end": u["end"], "title": u["title"], "kind": "go"} for u in parents]
            units = [u for u in units if all(u is not p for p in parents)]
    return units, containers


def extract(repo, files):
    """Parse {rel: lang} files. Return ({rel: (tests, containers, parse_errors)}, warnings).

    tests are inventory records; containers (start/end/title/kind dicts) and parse error byte
    ranges are internal, used by apply.
    """
    by_file = defaultdict(list)
    abs_to_rel = {os.path.abspath(os.path.join(repo, rel)): rel for rel in files}
    for m in astgrep.scan(RULES, sorted(abs_to_rel)):
        rel = abs_to_rel.get(os.path.abspath(m["file"]))
        if rel is not None:
            by_file[rel].append(m)
    result, warnings = {}, []
    for rel, lang in sorted(files.items()):
        matches = by_file.get(rel, [])
        try:
            with open(os.path.join(repo, rel), "rb") as fh:
                data = fh.read()
            data.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            warnings.append(f"skip {rel}: {exc.__class__.__name__}")
            continue
        errs = [(m["range"]["byteOffset"]["start"], m["range"]["byteOffset"]["end"]) for m in matches if m["ruleId"] == "err"]
        if lang == "py" and errs and py_compiles(data, rel):
            errs = []  # tree-sitter-python gap; CPython accepts the file
        if errs and lang != "ts":
            warnings.append(f"skip {rel}: parse error")
            continue
        units, containers = _parse_file(lang, data, [m for m in matches if m["ruleId"] != "err"])
        if errs:
            # tree-sitter flags some valid TS (e.g. `typeof import("x")` type args), so keep the
            # file but drop units that overlap a parse error: their ranges cannot be trusted.
            n = len(units)
            units = [u for u in units if not any(es < u["end"] and u["start"] < ee for es, ee in errs)]
            warnings.append(f"{rel}: {len(errs)} parse errors, dropped {n - len(units)} of {n} tests")
            if not units:
                continue
        units.sort(key=lambda u: (u["start"], -u["end"]))
        seen = defaultdict(int)
        tests = []
        for u in units:
            outer = sorted((c for c in containers + units if c is not u and c["start"] <= u["start"] and u["end"] <= c["end"]
                            and (c["start"], c["end"]) != (u["start"], u["end"])), key=lambda c: c["start"])
            path = [c["title"] for c in outer if c["title"] is not None] + [u["title"]]
            key = " > ".join(path)
            s, e = u["start"], u["end"]
            tests.append({"id": f"{rel}::{key}#{seen[key]}", "file": rel, "lang": lang, "title": u["title"], "path": path,
                          "occurrence": seen[key], "start_byte": s, "end_byte": e,
                          "start_line": data.count(b"\n", 0, s) + 1, "end_line": data.count(b"\n", 0, max(e - 1, s)) + 1,
                          "kind": "test"})
            seen[key] += 1
        result[rel] = (tests, containers, errs)
    return result, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--paths", nargs="+", help="only files matching these globs (relative to repo)")
    ap.add_argument("-o", "--out", default="inventory.jsonl")
    args = ap.parse_args(argv)
    files = find_files(args.repo, args.paths)
    result, warnings = extract(args.repo, files)
    counts = defaultdict(int)
    with open(args.out, "w", encoding="utf-8") as out:
        for rel in sorted(result):
            for t in result[rel][0]:
                out.write(json.dumps(t, ensure_ascii=False) + "\n")
                counts[t["lang"]] += 1
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(f"{sum(counts.values())} tests in {len(result)} files ({dict(sorted(counts.items()))}), "
          f"{len(files) - len(result)} files skipped -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
