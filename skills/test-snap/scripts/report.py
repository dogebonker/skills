#!/usr/bin/env python3
"""Build test-snap-report.md from inventory, decisions, the apply summary and timings.

Usage: report.py --inventory inventory.jsonl --decisions decisions.final.jsonl [--apply apply.txt]
       [--before before.json --after after.json] -o test-snap-report.md
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import compare_md  # noqa: E402

VERDICTS = ("delete", "review", "keep")


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def package(file):
    """Top-level package dir: the first two directory parts (apps/web, crates/core, tests)."""
    parts = PurePosixPath(file).parent.parts
    return "/".join(parts[:2]) or "."


def table(header, rows):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
                     + ["| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |" for r in rows])


def build(inventory, decisions, apply_summary=None, before=None, after=None):
    files = {t["id"]: t["file"] for t in inventory}
    verdicts = Counter(d["verdict"] for d in decisions)
    out = ["# Test snap report", "",
           f"{len(inventory)} tests inventoried in {len(set(files.values()))} files, {len(decisions)} judged.", "",
           "## Verdicts", "", table(["verdict", "tests"], [(v, verdicts[v]) for v in VERDICTS if verdicts[v]]), "",
           "## Categories", ""]
    cats = Counter((d["category"], d["verdict"]) for d in decisions)
    out += [table(["category", "verdict", "tests"], [(c, v, n) for (c, v), n in cats.most_common()]), ""]
    pkgs = {}
    for d in decisions:
        pkgs.setdefault(package(files.get(d["id"], d["id"].split("::")[0])), Counter())[d["verdict"]] += 1
    out += ["## By package", "", table(["package", "total", *VERDICTS],
            [(p, sum(c.values()), *(c[v] for v in VERDICTS)) for p, c in sorted(pkgs.items())]), ""]
    # Every guarded row, whether still `review` or already resolved by review.py or by hand.
    review = [d for d in decisions if d["verdict"] == "review" or d.get("guard")]
    out += [f"## Review ({len(review)})", ""]
    if review:
        out += [table(["id", "verdict", "guard", "reason"],
                      [(f"`{d['id']}`", d["verdict"], ", ".join(d.get("guard", [])), d.get("reason", ""))
                       for d in review]), ""]
    if apply_summary is not None:
        out += ["## Apply", "", "```", apply_summary.rstrip(), "```", ""]
    if before and after:
        out += ["## Timing", "", compare_md(before, after), ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--apply")
    ap.add_argument("--before")
    ap.add_argument("--after")
    ap.add_argument("-o", "--output", default="test-snap-report.md")
    a = ap.parse_args(argv)
    timing = [json.loads(Path(p).read_text()) if p else None for p in (a.before, a.after)]
    text = build(load_jsonl(a.inventory), load_jsonl(a.decisions),
                 Path(a.apply).read_text(encoding="utf-8") if a.apply else None, *timing)
    Path(a.output).write_text(text + "\n", encoding="utf-8")
    print(f"wrote {a.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
