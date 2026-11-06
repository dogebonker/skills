#!/usr/bin/env python3
"""Delete tests by verdict, remove emptied containers and files, revert files that stop parsing.

Usage: apply.py inventory.jsonl decisions.jsonl --repo <repo> [--verdicts delete ...] [--check]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import astgrep  # noqa: E402
import inventory  # noqa: E402

STD_BASES = re.compile(r"^(object|(\w+\.)*\w*TestCase)$")
ERR_RULES = "---\n".join(inventory.ERR_RULE.format(lang=l) for l in inventory.ALL_LANGS)


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _blank(line):
    return not line.strip()


def cut(data, s, e, repl=b""):
    """Remove data[s:e] (or replace it with `repl` lines) and tidy the blank lines around the cut."""
    ls = data.rfind(b"\n", 0, s) + 1
    le = data.find(b"\n", e)
    le = len(data) if le < 0 else le + 1
    tail = data[e:le].strip()
    if data[ls:s].strip() or (tail and not tail.startswith((b"//", b"#"))):
        return data[:s] + repl + data[e:]  # shares its line with other code: cut only the range
    nl = b"\r\n" if b"\r\n" in data else b"\n"
    if repl:
        indent = data[ls:s]
        return data[:ls] + b"".join(indent + r + nl for r in repl.split(b"\n")) + data[le:]
    head, rest = data[:ls], data[le:]
    before = head.splitlines(keepends=True)
    after = rest.splitlines(keepends=True)
    nb = 0
    while nb < len(before) and _blank(before[-1 - nb]):
        nb += 1
    na = 0
    while na < len(after) and _blank(after[na]):
        na += 1
    prev = before[-1 - nb].rstrip() if nb < len(before) else b""
    nxt = after[na].lstrip() if na < len(after) else b""
    keep = max(nb, na)
    if not prev or prev.endswith((b"{", b"(", b"[", b":")) or not nxt or nxt.startswith((b"}", b")", b"]")):
        keep = 0
    return b"".join(before[:len(before) - nb]) + nl * keep + b"".join(after[na:])


def _with_comments(data, s, lang):
    """Grow a cut over whole `//` (or `#` in Python) comment lines directly above it, so no
    orphaned note or `// @ts-expect-error` / `// eslint-disable-next-line` lands on the next test."""
    mark = b"#" if lang == "py" else b"//"
    while True:
        ls = data.rfind(b"\n", 0, s) + 1
        if ls == 0 or data[ls:s].strip():
            return s
        ps = data.rfind(b"\n", 0, ls - 1) + 1
        line = data[ps:ls - 1]
        if not line.strip().startswith(mark):
            return s
        s = ps + len(line) - len(line.lstrip())


def _go_own_code(data, c, cuts):
    """Whether a Go test function or t.Run body has code besides `cuts` (its subtests and the nested
    groups being removed) and comments."""
    body, pos = b"", c["start"]
    for s, e in sorted(cuts):
        body, pos = body + data[pos:max(pos, s)], max(pos, e)
    body += data[pos:c["end"]]
    body = re.sub(rb"//[^\n]*|/\*.*?\*/", b"", body, flags=re.S)
    return bool(body[body.find(b"{") + 1:body.rfind(b"}")].strip())


def plan(rel, lang, data, tests, containers, errs, delete_ids):
    """Return (edits, n_deleted, remaining, hollow) for one file. edits = [(start, end, replacement)];
    hollow = titles of emptied Go parents kept for code of their own."""
    def covered(s, e):
        return any(ds <= s and e <= de for ds, de in spans)

    spans = [(t["start_byte"], t["end_byte"]) for t in tests if t["id"] in delete_ids]
    if not spans:
        return [], 0, len(tests), []
    n_deleted = sum(1 for t in tests if covered(t["start_byte"], t["end_byte"]))
    remaining = len(tests) - n_deleted
    needs_pass, hollow = [], []
    for c in sorted(containers, key=lambda c: c["end"] - c["start"]):  # innermost first, so a parent sees its groups go
        inside = [t for t in tests if c["start"] <= t["start_byte"] and t["end_byte"] <= c["end"]]
        if not inside or covered(c["start"], c["end"]) or not all(covered(t["start_byte"], t["end_byte"]) for t in inside):
            continue
        if any(es < c["end"] and c["start"] < ee for es, ee in errs):
            continue  # may hold tests inventory dropped for overlapping a parse error
        if c["kind"] == "go" and _go_own_code(data, c, [(t["start_byte"], t["end_byte"]) for t in inside]
                                              + [sp for sp in spans if c["start"] <= sp[0] and sp[1] <= c["end"]]):
            hollow.append(c["title"])  # setup, helper checks or a t.Run table of its own: only the subtests go
            continue
        if c["kind"] == "class" and (not all(STD_BASES.match(b) for b in c["bases"])
                                     or re.search(rb"\b%s\b" % c["title"].encode(), data[:c["start"]] + data[c["end"]:])):
            needs_pass.append(c)  # inherits shared tests, or another class extends it: keep it
            continue
        spans.append((c["start"], c["end"]))
    spans = [sp for sp in spans if not any(o != sp and o[0] <= sp[0] and sp[1] <= o[1] for o in spans)]
    edits = [(_with_comments(data, s, lang), e, b"") for s, e in sorted(set(spans))]
    for c in needs_pass:  # Python class whose body would be empty gets `pass`
        own = [i for i, (s, e, _) in enumerate(edits) if c["start"] < s and e <= c["end"]]
        body, pos = b"", c["body_start"]
        for i in own:
            body += data[pos:max(pos, edits[i][0])]
            pos = max(pos, edits[i][1])
        body += data[pos:c["end"]]
        if own and not re.sub(rb"#[^\n]*", b"", body).strip():
            s, e, _ = edits[own[0]]
            edits[own[0]] = (s, e, b"pass")
    return edits, n_deleted, remaining, hollow


def deletable(rel, lang, new):
    """Whether a test file left with no tests can go, given its remaining text."""
    parts = rel.split("/")
    text = new.decode("utf-8", "replace")
    if lang == "ts":
        return not re.search(r"^export\b", text, re.M)  # another file may import its helpers
    if lang == "rs":
        return "tests" in parts[:-1] and parts[-1] != "mod.rs"  # src files only lose their test mod
    if lang == "go":  # same-package helpers may be used by other _test.go files
        text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"^\s*package\s+\w+|^\s*import\s*(\([^)]*\)|\S+)", "", text, flags=re.M)
        return not text.strip()
    if lang == "py":  # keep modules that still define helpers other tests may import
        for m in re.finditer(r"^(?:async\s+def|def|class)\s", text, re.M):
            prev = text[:m.start()].rstrip().rsplit("\n", 1)[-1]
            if not re.match(r"@\s*[\w.]*fixture\b", prev):
                return False
    return True


def _error_texts(paths):
    errs = {p: Counter() for p in paths}
    for m in astgrep.scan(ERR_RULES, paths):
        errs.setdefault(os.path.abspath(m["file"]), Counter())[m["text"]] += 1
    return errs


def _run(cmd, cwd):
    if not shutil.which(cmd[0]):
        return None
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1800)
    except (OSError, subprocess.TimeoutExpired):
        return None


def cleanup(repo, edited, ruff_dirty):
    """Run per-language cleanup on edited files. Returns report lines."""
    out = []
    by_lang = {}
    for rel, lang in edited.items():
        by_lang.setdefault(lang, []).append(rel)
    ts = by_lang.get("ts", [])
    # biome 2.x marks the noUnusedImports fix unsafe; --only keeps --unsafe scoped to that rule.
    if ts:
        r = _run(["npx", "-y", "@biomejs/biome", "lint", "--only=correctness/noUnusedImports", "--write", "--unsafe",
                  "--files-ignore-unknown=true", "--no-errors-on-unmatched", *ts], repo)
        out.append("biome noUnusedImports: " + ("skipped (npx missing)" if r is None else f"exit {r.returncode} on {len(ts)} files"))
    py = [f for f in by_lang.get("py", []) if f not in ruff_dirty]
    if by_lang.get("py"):
        r = _run(["ruff", "check", "--no-cache", "--select", "F401,F811,F841", "--fix", *py], repo) if py else None
        out.append("ruff F401,F811,F841: " + ("skipped (ruff missing)" if r is None and py else
                                              f"exit {r.returncode} on {len(py)} files" if r else "no files")
                   + (f", skipped {len(ruff_dirty)} files with unused imports before the edit" if ruff_dirty else ""))
        # A dropped import section leaves an extra blank line that isort flags (a Python repo: 15 I001 errors).
        # The repo's own config decides whether I001 is on; --fixable keeps the pass to import sorting.
        if r is not None:
            _run(["ruff", "check", "--no-cache", "--force-exclude", "--fix", "--fixable", "I001", *py], repo)
    rs = by_lang.get("rs", [])
    if rs:
        n = rust_unused_imports(repo, rs)
        out.append("rustc unused_imports: " + ("skipped (cargo missing)" if n is None else f"fixed {n} in {len(rs)} files"))
    go = by_lang.get("go", [])
    if go:
        r = _run(["gofmt", "-w", *go], repo)
        out.append("gofmt: " + ("skipped (gofmt missing)" if r is None else f"exit {r.returncode}"))
        r = _run(["go", "run", "golang.org/x/tools/cmd/goimports@latest", "-w", *go], repo)
        out.append("goimports: " + ("skipped (go missing)" if r is None else f"exit {r.returncode}"))
    return out


def rust_unused_imports(repo, rels):
    """Apply rustc's machine-applicable `unused_imports` fixes, only inside `rels` (no `cargo fix`, which
    would touch every file and every lint). Returns the number of imports fixed, or None without cargo."""
    r = _run(["cargo", "check", "--tests", "--message-format", "json"], repo)
    if r is None:
        return None
    targets = {os.path.normpath(os.path.join(repo, rel)): rel for rel in rels}
    fixes = {}  # rel -> {sorted span tuple}: one suggestion's spans go together (`{`, `, b`, `}`)
    for line in r.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = msg.get("message") or {}
        if msg.get("reason") != "compiler-message" or (m.get("code") or {}).get("code") != "unused_imports":
            continue
        for child in m.get("children", []):
            spans = [sp for sp in child.get("spans", []) if sp.get("suggestion_applicability") == "MachineApplicable"]
            rel = targets.get(os.path.normpath(os.path.join(repo, spans[0]["file_name"]))) if spans else None
            if rel and all(sp["file_name"] == spans[0]["file_name"] for sp in spans):
                fixes.setdefault(rel, set()).add(tuple(sorted((sp["byte_start"], sp["byte_end"],
                                                               sp["suggested_replacement"]) for sp in spans)))
    n = 0
    for rel, suggestions in fixes.items():  # the same diagnostic repeats once per target (lib, lib test)
        path = os.path.join(repo, rel)
        with open(path, "rb") as f:
            data = f.read()
        edits, taken = [], []
        for sug in sorted(suggestions):
            if any(s < e2 and s2 < e for s, e, _ in sug for s2, e2 in taken):
                continue
            edits += sug
            taken += [(s, e) for s, e, _ in sug]
            n += 1
        for s, e, repl in sorted(edits, reverse=True):
            data = data[:s] + repl.encode() + data[e:]
        with open(path, "wb") as f:
            f.write(data)
    return n


GO_UNUSED = re.compile(r"^(?:vet: )?([^\s:]+\.go):(\d+):(\d+): (?:declared and not used: (\w+)|(\w+) declared and not used)", re.M)
COMPILE_MSG = re.compile(r"^(?:vet: )?([^\s:]+\.(?:go|rs)):\d+:\d+: (.*)$", re.M)


def _build_errors(lang, repo, go_dirs):
    """({(abs file, message)}, tool output, [(abs file, line, col, name)] of unused Go locals) from
    `go vet` per package dir or `cargo check --tests`; (None, "", []) when the toolchain is missing."""
    runs = ([(["go", "vet", "."], os.path.join(repo, d)) for d in go_dirs] if lang == "go"
            else [(["cargo", "check", "--tests", "--message-format", "short"], repo)])
    errs, out, unused = set(), "", []
    for cmd, cwd in runs:
        r = _run(cmd, cwd)
        if r is None:
            return None, "", []
        out += r.stdout + r.stderr
        for path, msg in COMPILE_MSG.findall(r.stdout + r.stderr):
            if lang == "rs" and not msg.startswith("error"):
                continue
            errs.add((os.path.abspath(os.path.join(cwd, path)), msg))
        for path, ln, col, n1, n2 in GO_UNUSED.findall(r.stdout + r.stderr) if lang == "go" else []:
            unused.append((os.path.normpath(os.path.abspath(os.path.join(cwd, path))), int(ln), int(col), n1 or n2))
    return errs, out, unused


def go_blank_unused(path, line, col, name):
    """Rename an unused Go local to `_` (deleting a `t.Run` leaves the parent's setup unused, e.g.
    `c, srv := newClient(t)`); `:=` becomes `=` when no new name is left on its left side."""
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    row, c = lines[line - 1], col - 1
    if row[c:c + len(name.encode())] != name.encode():
        return False
    row = row[:c] + b"_" + row[c + len(name.encode()):]
    m = re.match(rb"^(\s*(?:for\s+|if\s+)?)([\w\s,]+?)\s*:=", row)
    if m and all(p.strip() == b"_" for p in m.group(2).split(b",")):
        row = row[:m.end() - 2] + b"=" + row[m.end():]
    lines[line - 1] = row
    with open(path, "wb") as f:
        f.write(b"\n".join(lines))
    return True


def verify_build(lang, repo, go_dirs, baseline, edited, originals):
    """Revert edited files the compiler blames for errors absent before the edit; re-check until clean.
    go vet stops at a package's first type error, hence the loop. Unused Go locals left by a deleted
    subtest are renamed to `_` first. Returns (reverted rels, report line)."""
    tool = "go vet" if lang == "go" else "cargo check --tests"
    reverted, blanked = [], set()
    while True:
        errs, out, unused = _build_errors(lang, repo, go_dirs)
        if errs is None:
            return reverted, f"{tool}: skipped ({'go' if lang == 'go' else 'cargo'} missing)"
        new = errs - baseline
        by_path = {os.path.normpath(os.path.abspath(os.path.join(repo, rel))): rel for rel, l in edited.items() if l == lang}
        fixed = False
        for ap, ln, col, name in unused:
            if ap in by_path and by_path[ap] not in reverted and (ap, ln, col) not in blanked:
                blanked.add((ap, ln, col))
                fixed |= go_blank_unused(ap, ln, col, name)
        if fixed:
            continue
        blamed = {by_path[p] for p, _ in new if p in by_path} - set(reverted)
        if not blamed:
            line = f"{tool}: {len(new)} new errors" + (f" (not in edited files: {sorted(new)[:5]})" if new else "")
            if lang == "rs":
                line += f", {out.count('unused import')} unused-import warnings"
            return reverted, line
        for rel in sorted(blamed):
            with open(os.path.join(repo, rel), "wb") as f:
                f.write(originals[rel])
            reverted.append(rel)


def ruff_baseline(repo, py_files):
    """Files that already have F401/F811 findings: `ruff --fix` there could drop pytest fixture imports."""
    if not py_files:
        return set()
    r = _run(["ruff", "check", "--no-cache", "--select", "F401,F811", "--output-format", "json", "--exit-zero", *py_files], repo)
    if r is None or r.returncode != 0:
        return set()
    return {os.path.relpath(d["filename"], os.path.abspath(repo)).replace(os.sep, "/") for d in json.loads(r.stdout or "[]")}


def apply(inv_rows, decisions, repo, verdicts=("delete",), check=False, run_cleanup=True):
    delete_ids = {d["id"] for d in decisions if d.get("verdict") in verdicts}
    files = {r["file"]: r["lang"] for r in inv_rows if r["id"] in delete_ids}
    fresh, warnings = inventory.extract(repo, files)
    found = {t["id"] for tests, _, _ in fresh.values() for t in tests}
    missing = sorted(delete_ids & {r["id"] for r in inv_rows} - found)
    ruff_dirty = ruff_baseline(repo, [f for f, l in files.items() if l == "py" and f in fresh])
    # Compiler baselines, so only errors the edit introduces count.
    go_dirs = sorted({os.path.dirname(rel) for rel in fresh if files[rel] == "go"})
    builds = {}
    # Unlocked `cargo check` can rewrite Cargo.lock (archgraph: it added the root package entry), and the
    # snap must change test files only. Restored at the end.
    lock_path = os.path.join(repo, "Cargo.lock")
    lock = open(lock_path, "rb").read() if os.path.isfile(lock_path) else None
    if go_dirs and shutil.which("go"):
        builds["go"] = _build_errors("go", repo, go_dirs)[0]
    if check and any(files[rel] == "rs" for rel in fresh):
        builds["rs"] = _build_errors("rs", repo, [])[0]
    lines, originals, edited, deleted_files, reverted = [], {}, {}, [], []
    n_by_file, hollow = {}, []
    for rel, (tests, containers, errs) in sorted(fresh.items()):
        path = os.path.join(repo, rel)
        with open(path, "rb") as f:
            data = f.read()
        edits, n, remaining, kept_parents = plan(rel, files[rel], data, tests, containers, errs, delete_ids)
        hollow += [f"{rel}::{title}" for title in kept_parents]
        if not edits:
            continue
        new = data
        for s, e, repl in sorted(edits, reverse=True):
            new = cut(new, s, e, repl)
        originals[rel] = data
        n_by_file[rel] = n
        if remaining == 0 and not errs and deletable(rel, files[rel], new):
            os.remove(path)
            deleted_files.append(rel)
            continue
        with open(path, "wb") as f:
            f.write(new)
        edited[rel] = files[rel]
    def revert_broken(stage):
        """Revert edited files that gained a parse error or stopped compiling (Python)."""
        abs_paths = {os.path.abspath(os.path.join(repo, rel)): rel for rel in edited}
        after = _error_texts(sorted(abs_paths))
        for ap, rel in abs_paths.items():
            before = Counter(originals[rel][s:e].decode("utf-8", "replace") for s, e in fresh[rel][2])
            reason = None
            if after.get(ap, Counter()) - before:
                reason = f"parse error after {stage}"
            elif edited[rel] == "py" and inventory.py_compiles(originals[rel], rel):
                with open(ap, "rb") as f:
                    if not inventory.py_compiles(f.read(), rel):
                        reason = f"py_compile failed after {stage}"
            if reason:
                with open(ap, "wb") as f:
                    f.write(originals[rel])
                reverted.append((rel, reason))
                del edited[rel], n_by_file[rel]

    revert_broken("edit")
    tool_lines = cleanup(repo, edited, ruff_dirty) if run_cleanup else []
    if run_cleanup:
        revert_broken("cleanup")  # biome, ruff or goimports must not leave a file broken either
    for lang, baseline in builds.items():  # after cleanup: goimports fixes unused imports first
        if baseline is None or lang not in edited.values():
            continue
        bad, line = verify_build(lang, repo, go_dirs, baseline, edited, originals)
        tool_lines.append(line)
        for rel in bad:
            reverted.append((rel, ("go vet" if lang == "go" else "cargo check") + " error after edit"))
            del edited[rel], n_by_file[rel]
    if lock is not None:
        with open(lock_path, "rb") as f:
            if f.read() != lock:
                with open(lock_path, "wb") as w:
                    w.write(lock)
    n_deleted = sum(n_by_file.values())
    lines.append(f"tests deleted: {n_deleted}")
    lines.append(f"files edited: {len(edited)}")
    lines.append(f"files deleted: {len(deleted_files)}")
    lines += [f"  deleted {rel}" for rel in deleted_files]
    lines.append(f"files reverted: {len(reverted)}")
    lines += [f"  reverted {rel}: {why}" for rel, why in reverted]
    if missing:
        lines.append(f"ids not found (file changed since inventory?): {len(missing)}")
        lines += [f"  missing {i}" for i in missing[:50]]
    if hollow:  # step 6: delete the ones left with setup only
        lines.append(f"Go parents emptied of subtests but kept for code of their own: {len(hollow)}")
        lines += [f"  kept {h}" for h in hollow]
    lines += [f"warning: {w}" for w in warnings]
    lines += tool_lines
    return {"tests_deleted": n_deleted, "edited": sorted(edited), "deleted": deleted_files,
            "reverted": reverted, "missing": missing, "lines": lines}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inventory")
    ap.add_argument("decisions")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--verdicts", nargs="+", default=["delete"])
    ap.add_argument("--check", action="store_true", help="Rust: run cargo check --tests after the edit")
    a = ap.parse_args(argv)
    result = apply(read_jsonl(a.inventory), read_jsonl(a.decisions), a.repo, tuple(a.verdicts), a.check)
    print("\n".join(result["lines"]))


if __name__ == "__main__":
    main()
