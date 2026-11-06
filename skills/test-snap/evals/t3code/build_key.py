"""Build the t3code answer key from the test snap PR (#22557).

Inventories the tree before the snap (c3540a7854) and after it (05696c636e),
labels each pre-snap test delete or keep by whether its (file, path) survives,
marks the must-keep tests, and draws a stratified file sample.

Each row carries two labels: `label` from the snap PR alone, and `settled` from main
after the team's follow-up prunes and restores (the reference the scorer uses).
Rows carry a split: train and holdout (the dev sample, split by file hash) and test
(a second sample drawn from the remaining files, scored once at the end).

usage: python3 -I build_key.py <t3code clone> [--files 200] [--test-files 100] [--seed 22557]
writes key.jsonl, sample.txt and inventory.pre.jsonl next to this script.
"""
import argparse
import collections
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INVENTORY = HERE.parents[1] / "scripts" / "inventory.py"
PRE, POST = "c3540a7854", "05696c636e"
SETTLED = "c58d558e10"  # main on 2026-10-23 after the second-pass prunes, #24058 and the four restores
PACKAGES = ["apps/server", "apps/web", "apps/mobile", "apps/desktop",
            "packages/client-runtime", "packages/shared", "packages/contracts"]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def inventory(tree, out):
    subprocess.run([sys.executable, "-I", str(INVENTORY), str(tree), "-o", str(out),
                    "--paths", *(pkg + "/*" for pkg in PACKAGES)], check=True)  # skips vendored .repos/
    return [json.loads(line) for line in Path(out).read_text().splitlines() if line.strip()]


def package(path):
    return next((p for p in PACKAGES if path.startswith(p + "/")), None)


def label(pre, post):
    """A pre-snap test is kept when its (file, path) still exists after the snap.
    Duplicate paths in a file: the first N survivors keep, the rest delete."""
    left = collections.Counter((t["file"], tuple(t["path"])) for t in post)
    out = {}
    for t in pre:
        key = (t["file"], tuple(t["path"]))
        out[t["id"]] = "keep" if left[key] > 0 else "delete"
        left[key] -= 1
    return out


def must_keep_ids(pre, entries):
    """Map must-keep entries (file + title) to pre-snap ids. A null title or a
    table-driven template title matches every test in the file whose last path
    part starts with the title's literal prefix."""
    by_file = collections.defaultdict(list)
    for t in pre:
        by_file[t["file"]].append(t)
    ids, missing = {}, []
    for e in entries:
        verified = ("candidate" if e["reason"].startswith("UNVERIFIED")
                    else "collateral" if e["reason"].startswith("COLLATERAL") else "verified")
        prefix = (e["title"] or "").split("${")[0].split("%")[0]
        hits = [t for t in by_file.get(e["file"], []) if t["title"].startswith(prefix)]
        if not hits:
            missing.append(e)
        for t in hits:
            ids[t["id"]] = verified
    return ids, missing


def sample(pre, must_files, n, seed):
    files = sorted({t["file"] for t in pre if package(t["file"])})
    by_pkg = collections.defaultdict(list)
    for f in files:
        by_pkg[package(f)].append(f)
    chosen = set(must_files)
    rng = random.Random(seed)
    room = n - len(chosen)
    for pkg in PACKAGES:  # proportional share, at least 5 files per package
        pool = [f for f in by_pkg[pkg] if f not in chosen]
        share = max(5, round(room * len(by_pkg[pkg]) / len(files)))
        chosen.update(rng.sample(pool, min(share, len(pool))))
    return sorted(chosen)


def dev_split(file):
    return "train" if hashlib.sha256(file.encode()).digest()[0] % 2 == 0 else "holdout"


def tree_inventory(repo, commit, tmp, name):
    tree = Path(tmp) / name
    git(repo, "worktree", "add", "--detach", str(tree), commit)
    try:
        return inventory(tree, Path(tmp) / f"{name}.jsonl")
    finally:
        git(repo, "worktree", "remove", "--force", str(tree))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--files", type=int, default=200)
    ap.add_argument("--test-files", type=int, default=100)
    ap.add_argument("--seed", type=int, default=22557)
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    if not git(repo, "rev-parse", "HEAD").startswith(PRE):
        sys.exit(f"check out {PRE} in {repo} first")
    with tempfile.TemporaryDirectory() as tmp:
        post = tree_inventory(repo, POST, tmp, "post")
        settled_tree = tree_inventory(repo, SETTLED, tmp, "settled")
    pre = inventory(repo, HERE / "inventory.pre.jsonl")
    labels, settled = label(pre, post), label(pre, settled_tree)
    must, missing = must_keep_ids(pre, json.loads((HERE / "must-keep.json").read_text()))
    for e in missing:
        print(f"must-keep not found in pre-snap tree: {e['file']} :: {e['title']}", file=sys.stderr)
    files = sample(pre, {t["file"] for t in pre if t["id"] in must}, a.files, a.seed)
    rest = [t for t in pre if t["file"] not in set(files)]
    test_files = sample(rest, set(), a.test_files, a.seed + 1)
    # test2: a second blind sample, drawn after test was spent in round 10
    test2_files = sample([t for t in rest if t["file"] not in set(test_files)], set(), a.test_files, a.seed + 2)
    (HERE / "sample.txt").write_text("\n".join(files) + "\n")
    (HERE / "sample.test.txt").write_text("\n".join(test_files) + "\n")
    (HERE / "sample.test2.txt").write_text("\n".join(test2_files) + "\n")
    split = {f: dev_split(f) for f in files} | {f: "test" for f in test_files} | {f: "test2" for f in test2_files}
    with open(HERE / "key.jsonl", "w") as fh:
        for t in pre:
            if t["file"] in split:
                row = {"id": t["id"], "split": split[t["file"]], "label": labels[t["id"]], "settled": settled[t["id"]]}
                if t["id"] in must:
                    row["must_keep"] = must[t["id"]]
                fh.write(json.dumps(row) + "\n")
    print(f"pre {len(pre)} tests, post {len(post)}, settled {len(settled_tree)}")
    for name in ("train", "holdout", "test", "test2"):
        rows = [settled[t["id"]] for t in pre if split.get(t["file"]) == name]
        print(f"{name}: {sum(v == name for v in split.values())} files, {len(rows)} tests, "
              f"settled delete rate {rows.count('delete') / len(rows):.1%}")


if __name__ == "__main__":
    main()
