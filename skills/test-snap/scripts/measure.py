#!/usr/bin/env python3
"""Time a test command and parse pass/fail counts, or compare two timings.

Usage: measure.py --repo <repo> --cmd "<test command>" [--runs 1] -o timing.json
       measure.py compare before.json after.json
"""
import argparse
import json
import re
import statistics
import subprocess
import sys
import time

ANSI = re.compile(r"\x1b\[[0-9;]*m")
TASK_PREFIX = re.compile(r"^(?:@[\w.-]+/)?[\w.-]+:[\w-]+: ?", re.M)  # turbo / nx `pkg:task: ` line prefix


def counts(pairs, mapping):
    out = {"passed": 0, "failed": 0, "skipped": 0}
    for n, word in pairs:
        if word in mapping:
            out[mapping[word]] += int(n)
    return out


def parse_pytest(text):
    lines = re.findall(r"^=*\s*((?:\d+ \w+,? ?)+) in [\d.]+s", text, re.M)
    if not lines:
        return None
    out = counts(re.findall(r"(\d+) (\w+)", lines[-1]), {"passed": "passed", "xpassed": "passed", "failed": "failed",
                 "error": "failed", "errors": "failed", "skipped": "skipped", "xfailed": "skipped"})
    out["failures"] = re.findall(r"^(?:FAILED|ERROR) (\S+)", text, re.M)
    return out


def parse_vitest(text):
    lines = re.findall(r"^\s*Tests\s+(.+?)\s+\(\d+\)\s*$", text, re.M)
    if not lines:
        return None
    out = counts([p for line in lines for p in re.findall(r"(\d+) (\w+)", line)],
                 {"passed": "passed", "failed": "failed", "skipped": "skipped", "todo": "skipped"})
    out["failures"] = [f.strip() for f in re.findall(r"^[ ]*FAIL[ ]+(\S.*)$", text, re.M)]
    return out


def parse_cargo(text):
    lines = re.findall(r"^test result: \w+\. (\d+) passed; (\d+) failed; (\d+) ignored", text, re.M)
    if not lines:
        return None
    out = {k: sum(int(line[i]) for line in lines) for i, k in enumerate(("passed", "failed", "skipped"))}
    out["failures"] = re.findall(r"^test (\S+) \.\.\. FAILED", text, re.M)
    return out


def parse_go(text):
    marks = re.findall(r"^\s*--- (PASS|FAIL|SKIP): (\S+)", text, re.M)
    pkgs = re.findall(r"^(ok|FAIL) *\t(\S+)", text, re.M)  # a tab follows, unlike TAP `ok 1 - name`
    if not marks and not pkgs:
        return None
    verbose = "=== RUN" in text  # without -v go prints only failures, so pass counts are unknown
    out = {"passed": sum(m == "PASS" for m, _ in marks) if verbose else None,
           "failed": sum(m == "FAIL" for m, _ in marks),
           "skipped": sum(m == "SKIP" for m, _ in marks) if verbose else None}
    out["failures"] = [n for m, n in marks if m == "FAIL"] + [f"package {p}" for s, p in pkgs if s == "FAIL"]
    out["packages_ok"] = sum(s == "ok" for s, _ in pkgs)
    out["packages_failed"] = sum(s == "FAIL" for s, _ in pkgs)
    return out


def parse_bun(text):
    if not re.search(r"^Ran \d+ tests? across \d+ files?\.", text, re.M):
        return None
    out = counts(re.findall(r"^ (\d+) (pass|fail|skip|todo)$", text, re.M),
                 {"pass": "passed", "fail": "failed", "skip": "skipped", "todo": "skipped"})
    # bun names only the failing test, so prefix the `path:` header it prints before each file's output.
    out["failures"], file = [], ""
    for line in text.splitlines():
        if re.match(r"^\S+\.[cm]?[jt]sx?:$", line):
            file = line[:-1]
        elif line.startswith("(fail) "):
            out["failures"].append(file + " > " + re.sub(r" \[[\d.]+m?s\]$", "", line[7:]))
        elif line == "# Unhandled error between tests":
            out["failures"].append(f"{file} > unhandled error")
    return out


def parse_unittest(text):
    runs = re.findall(r"^Ran (\d+) tests? in [\d.]+s\n\n(OK|FAILED)(?: \(([^)]*)\))?", text, re.M)
    if not runs:
        return None
    out = {"passed": 0, "failed": 0, "skipped": 0}
    for ran, _, detail in runs:
        n = {k.strip(): int(v) for k, v in re.findall(r"([a-z ]+)=(\d+)", detail)}
        failed = n.get("failures", 0) + n.get("errors", 0)
        skipped = n.get("skipped", 0) + n.get("expected failures", 0)
        out["failed"] += failed
        out["skipped"] += skipped
        out["passed"] += int(ran) - failed - skipped
    # `test_x (mod.Class)` before Python 3.11, `test_x (mod.Class.test_x)` after: name both the same way.
    out["failures"] = [cls if cls.endswith("." + name) else f"{cls}.{name}"
                       for name, cls in re.findall(r"^(?:FAIL|ERROR): (\w+) \(([\w.]+)\)", text, re.M)]
    return out


def parse_node_tap(text):
    """`node --test` TAP summary (the default reporter when stdout is not a terminal)."""
    lines = re.findall(r"^# (pass|fail|cancelled|skipped|todo) (\d+)$", text, re.M)
    if not re.search(r"^# tests \d+$", text, re.M) or not lines:
        return None
    out = counts([(n, w) for w, n in lines], {"pass": "passed", "fail": "failed", "cancelled": "failed",
                                              "skipped": "skipped", "todo": "skipped"})
    out["failures"] = [n.strip() for n in re.findall(r"^\s*not ok \d+ - (.+?)(?: # \w+.*)?$", text, re.M)]
    return out


PARSERS = {"pytest": parse_pytest, "vitest": parse_vitest, "cargo": parse_cargo, "go": parse_go, "bun": parse_bun,
           "unittest": parse_unittest, "node": parse_node_tap}


def parse(text):
    """Merge every runner summary found in the output (mixed repos run several)."""
    text = TASK_PREFIX.sub("", ANSI.sub("", text))
    merged = {"runner": None, "passed": None, "failed": None, "skipped": None, "failures": []}
    for name, fn in PARSERS.items():
        r = fn(text)
        if r is None:
            continue
        merged["runner"] = f"{merged['runner']}+{name}" if merged["runner"] else name
        for k, v in r.items():
            if k == "failures":
                merged[k] += v
            elif v is not None:
                merged[k] = (merged.get(k) or 0) + v
    return merged


def run(repo, cmd, runs):
    results, output = [], ""
    for _ in range(runs):
        start = time.monotonic()
        p = subprocess.run(cmd, shell=True, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, errors="replace")
        results.append({"wall_s": round(time.monotonic() - start, 3), "exit_code": p.returncode})
        output = p.stdout
    return {"cmd": cmd, "repo": repo, "runs": results, "wall_s": statistics.median(r["wall_s"] for r in results),
            "exit_code": results[-1]["exit_code"], **parse(output), "output_tail": output[-4000:]}


def compare_md(before, after):
    """Markdown before/after table, then new failures apart from pre-existing ones."""
    def cell(v):
        return "n/a" if v is None else str(v)

    lines = ["| metric | before | after | delta |", "|---|---|---|---|"]
    for k in ("wall_s", "passed", "failed", "skipped", "exit_code"):
        b, a = before.get(k), after.get(k)
        delta = round(a - b, 3) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else "n/a"
        lines.append(f"| {k} | {cell(b)} | {cell(a)} | {delta} |")
    old = set(before.get("failures") or [])
    new = [f for f in after.get("failures") or [] if f not in old]
    still = [f for f in after.get("failures") or [] if f in old]
    lines += ["", f"New failures (after, not before): {len(new)}", *[f"- {f}" for f in new],
              "", f"Pre-existing failures: {len(still)}", *[f"- {f}" for f in still]]
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["compare"]:
        ap = argparse.ArgumentParser(prog="measure.py compare")
        ap.add_argument("before")
        ap.add_argument("after")
        a = ap.parse_args(argv[1:])
        with open(a.before) as b, open(a.after) as f:
            print(compare_md(json.load(b), json.load(f)))
        return
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args(argv)
    result = run(a.repo, a.cmd, a.runs)
    with open(a.output, "w") as f:
        json.dump(result, f, indent=2)
    print(f"{result['wall_s']}s exit={result['exit_code']} runner={result['runner']} "
          f"passed={result['passed']} failed={result['failed']} skipped={result['skipped']}", file=sys.stderr)


if __name__ == "__main__":
    main()
