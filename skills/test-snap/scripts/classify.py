#!/usr/bin/env python3
"""Classify each inventoried test as delete or keep with an LLM, per file, with consensus and caching.

Usage: classify.py inventory.jsonl --repo <repo> -o decisions.jsonl [--model haiku] [--passes 1|2]
       [--double-fraction 0.5] [--concurrency 8] [--cache .test-snap-cache] [--max-files N] [--budget-usd X]
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUBRIC_PATH = Path(__file__).resolve().parent.parent / "references" / "rubric.md"
CHUNK = 60
INSTRUCTIONS = """

## Output

You get one test file and a list of test ids from it. Return exactly one entry per listed id, each id once.
`verdict` is `delete` or `keep`. `category` is one category name from the tables above that matches the verdict.
`reason` is one short line naming what the test checks and why that fits the category.
"""


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def classifier_rubric(rubric):
    """The rubric up to the guard's keyword lists and the reviewer's section, which the classifier never uses."""
    return rubric.split("\n## Sensitive keywords", 1)[0].split("\n## Review", 1)[0]


def rubric_categories(rubric):
    """Category names from the Delete and Keep tables, in order."""
    return re.findall(r"^\|\s*`([a-z-]+)`\s*\|", rubric, re.M)


def schema_for(ids, categories):
    return {
        "type": "object",
        "properties": {"tests": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "enum": ids},
                "verdict": {"type": "string", "enum": ["delete", "keep"]},
                "category": {"type": "string", "enum": categories},
                "reason": {"type": "string"},
            },
            "required": ["id", "verdict", "category", "reason"],
        }}},
        "required": ["tests"],
    }


def claude_llm(system, prompt, schema, model, tools="", cwd=None, max_turns=None):
    """Real call. Returns (structured_output or None, reported cost in USD).

    `tools` other than "" are pre-approved inside `cwd` only and everything else is denied (dontAsk), so no
    prompt can block and a prompt-injected test file cannot read outside the repo (an unscoped `Read`
    rule was verified to read a file outside cwd).
    """
    # --setting-sources "" keeps user hooks, plugins and CLAUDE.md out of the call (verified: 7.7k -> 1.3k input tokens).
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--json-schema", json.dumps(schema),
           "--tools", tools, "--strict-mcp-config", "--no-session-persistence", "--setting-sources", "",
           "--system-prompt", system]
    if tools:
        cmd += ["--allowedTools", ",".join(f"{t}(./**)" for t in tools.split(",")), "--permission-mode", "dontAsk"]
    if max_turns:
        cmd += ["--max-turns", str(max_turns)]
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=900, cwd=cwd)
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude exit {p.returncode}: {(p.stderr or p.stdout)[-300:]}")
    return out.get("structured_output"), float(out.get("total_cost_usd") or 0)


def validate(result, ids, categories):
    """Return the result rows by id when every id is covered exactly once with valid fields, else None."""
    rows = result.get("tests") if isinstance(result, dict) else None
    if not isinstance(rows, list):
        return None
    by_id = {}
    for r in rows:
        if (not isinstance(r, dict) or r.get("id") not in ids or r["id"] in by_id
                or r.get("verdict") not in ("delete", "keep") or r.get("category") not in categories):
            return None
        by_id[r["id"]] = {"verdict": r["verdict"], "category": r["category"], "reason": str(r.get("reason", ""))}
    return by_id if len(by_id) == len(ids) else None


def is_double(file, fraction):
    return int(hashlib.sha256(file.encode()).hexdigest()[:8], 16) / 2**32 < fraction


class Judge:
    """One validated LLM pass over a chunk, with cache, retry and a shared budget."""

    NOT_JUDGED = "not-judged"

    def __init__(self, llm, model, rubric, cache_dir=None, budget=None, system=None):
        self.llm, self.model, self.rubric = llm, model, rubric
        self.system = system or classifier_rubric(rubric) + INSTRUCTIONS
        self.categories = rubric_categories(rubric)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.budget, self.spent, self.calls = budget, 0.0, 0
        self.lock = threading.Lock()

    def __call__(self, file, content, tests, pass_idx):
        """Return {id: row}, None on classifier failure, or NOT_JUDGED when the budget is spent."""
        ids = [t["id"] for t in tests]
        listing = "\n".join(f"- {t['id']}  (lines {t['start_line']}-{t['end_line']})" for t in tests)
        prompt = f"File: {file}\n\n```\n{content}\n```\n\nJudge these test ids:\n{listing}\n"
        return self.ask(file, [content, ids, pass_idx], prompt, schema_for(ids, self.categories),
                        lambda result: validate(result, set(ids), self.categories))

    def ask(self, label, key_parts, prompt, schema, check):
        """Cached, budgeted call with one retry. `check` returns the validated value or None."""
        key = hashlib.sha256(json.dumps([self.model, self.system, *key_parts]).encode()).hexdigest()
        cached = self.cache_dir / f"{key}.json" if self.cache_dir else None
        if cached and cached.exists():
            return json.loads(cached.read_text())
        for _ in range(2):
            with self.lock:
                if self.budget is not None and self.spent >= self.budget:
                    return self.NOT_JUDGED
            try:
                result, cost = self.llm(self.system, prompt, schema, self.model)
            except Exception as e:  # a crashed call counts as a failed attempt
                print(f"  {label}: call failed: {e}", file=sys.stderr)
                result, cost = None, 0.0
            with self.lock:
                self.spent += cost
                self.calls += 1
            rows = check(result)
            if rows is not None:
                if cached:
                    cached.parent.mkdir(parents=True, exist_ok=True)
                    cached.write_text(json.dumps(rows))
                return rows
        return None


def fallback(ids, category, reason, votes=None):
    return {i: {"verdict": "keep", "category": category, "reason": reason, "votes": votes or []} for i in ids}


def decide_chunk(judge, file, content, tests, double):
    """Consensus: single pass takes the one verdict, double pass deletes only on agreement, tiebreak by majority."""
    ids = [t["id"] for t in tests]
    passes = []
    for idx in range(2 if double else 1):
        r = judge(file, content, tests, idx)
        if r is None:
            return fallback(ids, "classifier-error", "classifier output failed validation twice")
        if r is Judge.NOT_JUDGED:
            return fallback(ids, Judge.NOT_JUDGED, "budget reached before this file was judged")
        passes.append(r)
    split = [t for t in tests if len({p[t["id"]]["verdict"] for p in passes}) > 1]
    tiebreak = judge(file, content, split, 2) if split else {}
    if tiebreak is None or tiebreak is Judge.NOT_JUDGED:  # fail safe: no tiebreak means keep
        cat = "classifier-error" if tiebreak is None else Judge.NOT_JUDGED
        tiebreak = {t["id"]: {"verdict": "keep", "category": cat, "reason": "passes disagreed, no tiebreak"}
                    for t in split}
        passes.append({i: {**v, "abstain": True} for i, v in tiebreak.items()})
    else:
        passes.append(tiebreak)
    out = {}
    for i in ids:
        votes = [p[i] for p in passes if i in p]
        verdict = "delete" if sum(v["verdict"] == "delete" for v in votes) * 2 > len(votes) else "keep"
        pick = next(v for v in reversed(votes) if v["verdict"] == verdict)
        out[i] = {"verdict": verdict, "category": pick["category"], "reason": pick["reason"],
                  "votes": [v["verdict"] for v in votes if not v.get("abstain")]}
    return out


def classify(inventory, repo, judge, passes=2, double_fraction=0.5, concurrency=8, max_files=None):
    """Return decision rows in inventory order."""
    by_file = {}
    for t in inventory:
        by_file.setdefault(t["file"], []).append(t)
    files = list(by_file)
    judged = set(files[:max_files] if max_files is not None else files)
    jobs = [(f, by_file[f][i:i + CHUNK]) for f in files for i in range(0, len(by_file[f]), CHUNK)]
    done, results, lock = [0], {}, threading.Lock()

    def run(job):
        file, tests = job
        if file not in judged:
            res = fallback([t["id"] for t in tests], Judge.NOT_JUDGED, "outside --max-files")
        else:
            content = (Path(repo) / file).read_text(encoding="utf-8", errors="replace")
            res = decide_chunk(judge, file, content, tests, passes == 2 and is_double(file, double_fraction))
        with lock:
            results.update(res)
            done[0] += 1
            dels = sum(r["verdict"] == "delete" for r in res.values())
            print(f"[{done[0]}/{len(jobs)}] {file}: {dels}/{len(res)} delete, spent ${judge.spent:.4f}",
                  file=sys.stderr)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(run, jobs))
    return [{"id": t["id"], **results[t["id"]]} for t in inventory]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inventory")
    ap.add_argument("--repo", required=True)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--passes", type=int, choices=(1, 2), default=2)
    ap.add_argument("--double-fraction", type=float, default=0.5)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--cache", default=".test-snap-cache")
    ap.add_argument("--max-files", type=int)
    ap.add_argument("--budget-usd", type=float)
    a = ap.parse_args(argv)
    judge = Judge(claude_llm, a.model, RUBRIC_PATH.read_text(encoding="utf-8"), a.cache, a.budget_usd)
    rows = classify(load_jsonl(a.inventory), a.repo, judge, a.passes, a.double_fraction, a.concurrency, a.max_files)
    with open(a.output, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(f"{len(rows)} tests, {counts}, {judge.calls} calls, ${judge.spent:.4f}", file=sys.stderr)


if __name__ == "__main__":
    main()
