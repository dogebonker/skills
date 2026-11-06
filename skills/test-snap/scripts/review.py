#!/usr/bin/env python3
"""Resolve `review` rows with a stronger model that can read the repo, one call per test file.

Usage: review.py inventory.jsonl decisions.guarded.jsonl --repo <repo> -o decisions.final.jsonl
       [--model sonnet] [--concurrency 4] [--cache DIR] [--budget-usd N]
"""
import argparse
import functools
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify  # noqa: E402

TOOLS = "Read,Grep,Glob"  # read-only: no Write, Edit or Bash, and dontAsk denies anything else
MAX_TURNS = 15
INSTRUCTIONS = """

## Output

Return exactly one entry per listed id, each id once. `verdict` is `keep` or `delete`.
`reason` is one line that names the behavior and why it is kept or deleted.
`covered_by` is the repo path of the kept test that already checks the behavior, or null.
`evidence` is one line copied exactly from that covering test that sets up or asserts the same input or state, or null.
"""


def reviewer_rubric(rubric):
    """The rubric without the guard's keyword lists, which only guard.py reads."""
    head, rest = rubric.split("\n## Sensitive keywords", 1)
    return head + "\n## Review" + rest.split("\n## Review", 1)[1]


def schema_for(ids):
    return {
        "type": "object",
        "properties": {"tests": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "enum": ids},
                "verdict": {"type": "string", "enum": ["keep", "delete"]},
                "reason": {"type": "string"},
                "covered_by": {"type": ["string", "null"]},
                "evidence": {"type": ["string", "null"]},
            },
            "required": ["id", "verdict", "reason", "covered_by", "evidence"],
        }}},
        "required": ["tests"],
    }


def validate(result, ids):
    rows = result.get("tests") if isinstance(result, dict) else None
    if not isinstance(rows, list):
        return None
    by_id = {}
    for r in rows:
        if (not isinstance(r, dict) or r.get("id") not in ids or r["id"] in by_id
                or r.get("verdict") not in ("keep", "delete")
                or not isinstance(r.get("covered_by"), (str, type(None)))
                or not isinstance(r.get("evidence"), (str, type(None)))):
            return None
        # capped: model text reaches the report and possibly a PR body
        by_id[r["id"]] = {"verdict": r["verdict"], "reason": str(r.get("reason", ""))[:300],
                          "covered_by": r["covered_by"], "evidence": (r.get("evidence") or None) and r["evidence"][:300]}
    return by_id if len(by_id) == len(ids) else None


def review_file(judge, file, content, rows, tests):
    """{id: {verdict, reason, covered_by}}, None on failure, or Judge.NOT_JUDGED."""
    ids = [r["id"] for r in rows]
    listing = "\n".join(
        f"- {r['id']}  (lines {tests[r['id']]['start_line']}-{tests[r['id']]['end_line']})\n"
        f"  classifier: {r.get('category')}: {r.get('reason')}\n  guard: {', '.join(r.get('guard', []))}"
        for r in rows)
    prompt = f"File: {file}\n\n```\n{content}\n```\n\nReview these tests:\n{listing}\n"
    key = [content, [[r["id"], r.get("category"), r.get("reason"), r.get("guard")] for r in rows]]
    return judge.ask(file, key, prompt, schema_for(ids), lambda result: validate(result, set(ids)))


def review(inventory, decisions, repo, judge, concurrency=4):
    """Return decision rows with review rows resolved; failures stay `review` with a `review_note`."""
    tests = {t["id"]: t for t in inventory}
    by_file = {}
    for d in decisions:
        if d["verdict"] == "review" and d["id"] in tests:
            by_file.setdefault(tests[d["id"]]["file"], []).append(d)
    results, done, lock = {}, [0], threading.Lock()

    def run(file):
        content = (Path(repo) / file).read_text(encoding="utf-8", errors="replace")
        res = review_file(judge, file, content, by_file[file], tests)
        if res is None or res is classify.Judge.NOT_JUDGED:
            note = "classifier-error" if res is None else classify.Judge.NOT_JUDGED
            res = {d["id"]: {"review_note": note} for d in by_file[file]}
        with lock:
            results.update(res)
            done[0] += 1
            dels = sum(r.get("verdict") == "delete" for r in res.values())
            print(f"[{done[0]}/{len(by_file)}] {file}: {dels}/{len(res)} delete, spent ${judge.spent:.4f}",
                  file=sys.stderr)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(run, by_file))
    rows = [{**d, **results[d["id"]]} if d["id"] in results else d for d in decisions]
    return enforce_all(rows, inventory, repo)


def enforce_all(rows, inventory, repo):
    """Apply `enforce` until stable: a flip to keep can make another row's cover survive."""
    while True:
        verdicts = {r["id"]: r["verdict"] for r in rows}
        survivors = {}
        for t in inventory:
            if verdicts.get(t["id"], "keep") != "delete":
                survivors.setdefault(t["file"], []).append(t)
        new = [enforce(r, repo, survivors) for r in rows]
        if [r["verdict"] for r in new] == [r["verdict"] for r in rows]:
            return new
        rows = new


def enforce(row, repo, survivors):
    """A reviewed delete must prove cover when it can leave a behavior with no test at all (D18):
    a test a fix commit added, or the last test of a production symbol in a file it empties.
    The reviewer names the covering file and quotes a line (`evidence`) that sets up or
    asserts the same input or state. The quote must sit inside a test whose final verdict
    is not delete. Otherwise the delete becomes keep. In t3code the reviewer deleted the
    only tests of a panel, of createRenderScheduler, and a heading-parsing fix test whose
    claimed cover never used those headings.
    `survivors` maps a file to its inventoried tests that are not being deleted.
    """
    if row.get("verdict") != "delete" or not row.get("guard"):
        return row
    emptied_file = any(g.startswith("empties:") and "::" not in g for g in row["guard"])
    fix = any(g.startswith("fix-commit:") for g in row["guard"])
    last_of_symbol = emptied_file and any(g.startswith("sole-guard:") for g in row["guard"])
    if not fix and not last_of_symbol:
        return row  # other guarded deletes may drop presentational or variant behavior without a cover
    cover_file = (row.get("covered_by") or "").split("::")[0]
    quote = squash(row.get("evidence") or "")
    path = Path(repo) / cover_file
    if cover_file and len(quote) >= 12 and path.is_file():
        text = path.read_bytes()
        for t in survivors.get(cover_file, []):
            if t["id"] != row["id"] and quote in squash(text[t["start_byte"]:t["end_byte"]].decode("utf-8", "replace")):
                return row
    return {**row, "verdict": "keep",
            "reason": f"kept: delete named no covering test that survives ({row.get('reason', '')})"}


def squash(text):
    return " ".join(text.split())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inventory")
    ap.add_argument("decisions")
    ap.add_argument("--repo", required=True)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--cache", default=".test-snap-cache")
    ap.add_argument("--budget-usd", type=float)
    a = ap.parse_args(argv)
    rubric = classify.RUBRIC_PATH.read_text(encoding="utf-8")
    llm = functools.partial(classify.claude_llm, tools=TOOLS, cwd=a.repo, max_turns=MAX_TURNS)
    judge = classify.Judge(llm, a.model, rubric, a.cache, a.budget_usd, system=reviewer_rubric(rubric) + INSTRUCTIONS)
    rows = review(classify.load_jsonl(a.inventory), classify.load_jsonl(a.decisions), a.repo, judge, a.concurrency)
    with open(a.output, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(f"{len(rows)} rows, {counts}, {judge.calls} calls, ${judge.spent:.4f}", file=sys.stderr)


if __name__ == "__main__":
    main()
