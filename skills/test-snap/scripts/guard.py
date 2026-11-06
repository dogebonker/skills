#!/usr/bin/env python3
"""Move risky delete verdicts to review: sensitive keywords, sole guards, emptied containers, fix commits.

Usage: guard.py inventory.jsonl decisions.jsonl --repo <repo> -o decisions.guarded.jsonl [--no-history]
"""
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUBRIC_PATH = Path(__file__).resolve().parent.parent / "references" / "rubric.md"
TESTISH = re.compile(r"test|spec|mock|fixture|vitest|jest|testing|assert", re.I)
KEYWORDS = {  # call-like tokens that are syntax or test scaffolding, never production identifiers
    "if", "for", "while", "switch", "match", "return", "catch", "function", "fn", "func", "def", "await",
    "async", "new", "typeof", "sizeof", "loop", "in", "not", "and", "or", "lambda", "yield", "assert",
    "it", "test", "describe", "expect", "suite", "Some", "Ok", "Err", "Box", "Vec", "String", "make", "len",
    "append", "panic", "print", "range", "str", "int", "list", "dict", "set", "tuple", "isinstance",
}
IDENT = re.compile(r"[A-Za-z_]\w*")
FIX_SUBJECT = re.compile(r"^(fix|hotfix|bugfix)(\(.*\))?!?:", re.I)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def sensitive_keywords(rubric):
    """{word: "hard" | "soft"} from the two comma lists under '## Sensitive keywords' (hard first)."""
    section = rubric.split("## Sensitive keywords", 1)[1].split("\n## ", 1)[0]
    lists = [line for line in section.splitlines() if line.count(",") >= 3]
    return {w.strip().strip(".").lower(): tier for tier, line in zip(("hard", "soft"), lists)
            for w in line.split(",") if w.strip()}


def word_parts(text):
    """Lowercase word parts of a path or title; camelCase, snake_case and kebab-case split."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return [w.lower() for w in re.split(r"[^A-Za-z0-9]+", text) if w]


def sensitive_hits(test, keywords):
    parts = set(word_parts(test["file"] + " " + " ".join(test["path"])))
    return [k for k in keywords if any(p == k + s for p in parts for s in ("", "s", "es", "d", "ed"))]


def imports(src, lang):
    """(names, namespaces) imported from non-test production modules in one test file.

    ponytail: lexical regexes, no resolution. Misses CommonJS require, re-exports, Rust crate-name paths and
    Go dot-imports; counts bare npm packages and third-party Python as production. Upgrade: resolve modules
    against the repo tree, or use ast-grep for import nodes.
    """
    names, spaces = set(), set()
    if lang in ("ts", "tsx", "js", "jsx"):
        for clause, mod in re.findall(r"import\s+(?:type\s+)?([^'\";]*?)\s+from\s+['\"]([^'\"]+)['\"]", src, re.S):
            if TESTISH.search(mod) or mod.startswith("node:"):
                continue
            ns = re.search(r"\*\s+as\s+(\w+)", clause)
            if ns:
                spaces.add(ns.group(1))
            default = re.match(r"\s*(\w+)", clause)
            if default and default.group(1) != "type":
                names.add(default.group(1))
            braces = re.search(r"\{([^}]*)\}", clause)
            for item in (braces.group(1).split(",") if braces else []):
                item = re.sub(r"^\s*type\s+", "", item).strip()
                if item:
                    names.add(item.split(" as ")[-1].strip())
    elif lang == "py":
        stdlib = sys.stdlib_module_names
        for mod, paren, line in re.findall(r"^\s*from\s+([\w.]+)\s+import\s+(?:\(([^)]*)\)|([^\n]+))", src, re.M):
            if TESTISH.search(mod) or mod.split(".")[0] in stdlib:
                continue
            for item in re.sub(r"#.*", "", paren or line).replace("\n", ",").split(","):
                item = item.strip()
                if item and item != "*":
                    names.add(item.split(" as ")[-1].strip())
        for mod, alias in re.findall(r"^\s*import\s+([\w.]+)(?:\s+as\s+(\w+))?", src, re.M):
            if not (TESTISH.search(mod) or mod.split(".")[0] in stdlib):
                spaces.add(alias or mod.split(".")[0])
    elif lang == "rs":
        for path in re.findall(r"\buse\s+((?:crate|super|self)::[^;]+);", src):
            if TESTISH.search(path.rsplit("::", 1)[0]):
                continue
            tail = re.search(r"\{([^}]*)\}\s*$", path)
            for item in (tail.group(1).split(",") if tail else [path.rsplit("::", 1)[-1]]):
                item = item.strip().split("::")[-1]
                if item and item not in ("*", "self"):
                    names.add(item.split(" as ")[-1].strip())
    elif lang == "go":
        block = re.findall(r"^import\s*\(([^)]*)\)", src, re.M | re.S)
        specs = re.findall(r"^import\s+((?:\w+\s+)?\"[^\"]+\")", src, re.M) + "\n".join(block).splitlines()
        for spec in specs:
            m = re.match(r"\s*(\w+\s+)?\"([^\"]+)\"", spec)
            if not m or "." not in m.group(2).split("/")[0] or TESTISH.search(m.group(2)):
                continue  # stdlib paths have no dot in the first segment
            spaces.add((m.group(1) or m.group(2).rsplit("/", 1)[-1]).strip())
    return names, spaces


def local_defs(src):
    """Names defined in the test file itself (helpers, the tests), which are not production code."""
    return set(re.findall(r"\b(?:function|def|fn|func|const|let|var|class|struct|type)\s+(?:\([^)]*\)\s*)?(\w+)", src))


def references(body, lang, names, spaces, defs):
    """Production identifiers one test body refers to."""
    refs = {t for t in IDENT.findall(body) if t in names}
    refs |= {f"{ns}.{m}" for ns, m in re.findall(r"\b(\w+)\.(\w+)", body) if ns in spaces}
    # Rust `use super::*` and same-package Go tests reach production code by plain calls.
    if lang in ("rs", "go"):
        refs |= {c for c in re.findall(r"(?<![.\w:])([A-Za-z_]\w*)\s*\(", body) if c not in KEYWORDS}
    return refs - defs - KEYWORDS


def test_refs(inventory, repo):
    """{test id: set of production identifiers referenced}."""
    by_file, out = {}, {}
    for t in inventory:
        by_file.setdefault(t["file"], []).append(t)
    for file, tests in by_file.items():
        raw = (Path(repo) / file).read_bytes()
        src = raw.decode("utf-8", errors="replace")
        names, spaces = imports(src, tests[0]["lang"])
        # Rust tests live beside production code: only names defined in the test module are local.
        defs = local_defs(src[src.find("#[cfg(test)]"):] if "#[cfg(test)]" in src else src)
        for t in tests:
            body = raw[t["start_byte"]:t["end_byte"]].decode("utf-8", errors="replace")
            out[t["id"]] = references(body, t["lang"], names, spaces, defs)
    return out


def empties(test, kept):
    """The outermost scope (file, then describe/class/mod/t.Run parents) left with no kept test, or None."""
    if test["file"] not in kept:
        return test["file"]
    for k in range(1, len(test["path"])):
        if (test["file"], tuple(test["path"][:k])) not in kept:
            return f"{test['file']}::{' > '.join(test['path'][:k])}"
    return None


def is_fix(subject):
    s = subject.lower()
    return bool(FIX_SUBJECT.match(subject)) or "regression" in s or (re.search(r"#\d+", s) and "fix" in s)


def adding_commit(repo, test):
    """'<sha> <subject>' of the commit that introduced the test title in its file, or None."""
    # ponytail: --follow tracks one rename chain (git's similarity threshold) and breaks with --reverse,
    # so the oldest hit is the last line. Titles moved between files, edited since, or escaped in source are missed.
    p = subprocess.run(["git", "-C", str(repo), "log", "--follow", f"-S{test['title']}", "--format=%h %s",
                        "--", test["file"]], capture_output=True, text=True, errors="replace")
    lines = p.stdout.strip().splitlines()
    return lines[-1] if p.returncode == 0 and lines else None


def fix_commits(repo, tests, workers=8):
    """{test id: '<sha> <subject>'} for tests whose title came in with a fix commit. Empty outside git."""
    inside = subprocess.run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"], capture_output=True)
    if inside.returncode != 0 or not tests:
        return {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        found = dict(zip((t["id"] for t in tests), pool.map(lambda t: adding_commit(repo, t), tests)))
    return {i: c for i, c in found.items() if c and is_fix(c.split(" ", 1)[-1])}


def guard(inventory, decisions, repo, keywords, history=True):
    """Return decision rows with risky deletes moved to review and a `guard` list of reasons."""
    tests = {t["id"]: t for t in inventory}
    refs = test_refs(inventory, repo)
    verdicts = {d["id"]: d["verdict"] for d in decisions}
    kept, kept_scopes = set(), set()
    for t in inventory:  # a test with no decision (outside the judged files) stays, so it counts as kept
        if verdicts.get(t["id"], "keep") == "keep":
            kept |= refs.get(t["id"], set())
            kept_scopes.add(t["file"])
            kept_scopes.update((t["file"], tuple(t["path"][:k])) for k in range(1, len(t["path"]) + 1))
    candidates = [tests[d["id"]] for d in decisions if d["verdict"] == "delete" and d["id"] in tests]
    fixes = fix_commits(repo, candidates) if history else {}
    out = []
    for d in decisions:
        d = dict(d)
        t = tests.get(d["id"])
        if d["verdict"] == "delete" and t:
            why = [f"sensitive:{k}" for k in sensitive_hits(t, keywords)]
            why += [f"sole-guard:{i}" for i in sorted(refs[d["id"]] - kept)]
            scope = empties(t, kept_scopes)
            why += [f"empties:{scope}"] if scope else []
            why += [f"fix-commit:{fixes[t['id']]}"] if t["id"] in fixes else []
            if any(w.startswith("sensitive:") and keywords[w.split(":", 1)[1]] == "hard" for w in why):  # D12, D18
                d["verdict"], d["category"], d["guard"] = "keep", "security", why
                d["reason"] = "sensitive area, kept without review: " + d.get("reason", "")
            elif why:
                d["verdict"], d["guard"] = "review", why
        out.append(d)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inventory")
    ap.add_argument("decisions")
    ap.add_argument("--repo", required=True)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--no-history", action="store_true", help="skip the git fix-commit check")
    a = ap.parse_args(argv)
    keywords = sensitive_keywords(RUBRIC_PATH.read_text(encoding="utf-8"))
    rows = guard(load_jsonl(a.inventory), load_jsonl(a.decisions), a.repo, keywords, not a.no_history)
    with open(a.output, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    moved = [r for r in rows if r.get("guard")]
    kinds = ", ".join(f"{sum(any(g.startswith(k + ':') for g in r['guard']) for r in moved)} {k}"
                      for k in ("sensitive", "sole-guard", "empties", "fix-commit"))
    print(f"{len(moved)} deletes moved to review ({kinds})", file=sys.stderr)


if __name__ == "__main__":
    main()
