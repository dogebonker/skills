"""Score decisions against the t3code answer key.

usage: python3 -I score.py <decisions.jsonl> [--key key.jsonl] [--json]

The reference for precision and recall is the team's settled result (main after
the snap, the second-pass prunes and the restores). Must-keep rows are tests the
team restored (verified), restored only as part of a verbatim file restore
(collateral), or picked as likely auth restores (candidate). Gates: no verified
must-keep deleted (G1), and on the test split F1 >= 0.65 with a delete rate
within 15 points of the reference (G4).
`review` counts as not deleted: the orchestrating agent judges those rows.
"""
import argparse
import json
from pathlib import Path


def load(path):
    return {r["id"]: r for r in map(json.loads, Path(path).read_text().splitlines()) if r}


def score(decisions, key, ref="settled"):
    tp = fp = fn = tn = 0
    review = unjudged = 0
    must = {"verified": [0, 0], "candidate": [0, 0], "collateral": [0, 0]}  # [deleted, total]
    review_hits = {"verified": 0, "candidate": 0, "collateral": 0}
    for tid, k in key.items():
        d = decisions.get(tid)
        verdict = d["verdict"] if d else "keep"
        unjudged += d is None
        review += verdict == "review"
        deleted = verdict == "delete"
        if k[ref] == "delete":
            tp += deleted
            fn += not deleted
        else:
            fp += deleted
            tn += not deleted
        if "must_keep" in k:
            must[k["must_keep"]][0] += deleted
            must[k["must_keep"]][1] += 1
            review_hits[k["must_keep"]] += verdict == "review"
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    total = len(key)
    return {
        "tests": total, "unjudged": unjudged,
        "ref_delete_rate": round((tp + fn) / total, 3),
        "delete_rate": round((tp + fp) / total, 3),
        "review_rate": round(review / total, 3),
        "precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3),
        "must_keep_verified_deleted": must["verified"][0],
        "must_keep_verified_total": must["verified"][1],
        "must_keep_verified_in_review": review_hits["verified"],
        "must_keep_candidate_deleted": must["candidate"][0],
        "must_keep_candidate_total": must["candidate"][1],
        "must_keep_collateral_deleted": must["collateral"][0],
        "must_keep_collateral_total": must["collateral"][1],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("decisions")
    ap.add_argument("--key", default=Path(__file__).with_name("key.jsonl"))
    ap.add_argument("--split", choices=["all", "dev", "train", "holdout", "test", "test2"], default="dev")
    ap.add_argument("--ref", choices=["settled", "label"], default="settled",
                    help="settled: main after the team's follow-ups (default), label: the snap PR alone")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    want = {"all": {"train", "holdout", "test", "test2"}, "dev": {"train", "holdout"}}.get(a.split, {a.split})
    key = {k: v for k, v in load(a.key).items() if v["split"] in want}
    s = score(load(a.decisions), key, a.ref)
    if a.json:
        print(json.dumps(s, indent=2))
        return
    for k, v in s.items():
        print(f"{k:32} {v}")
    fails = []
    if s["must_keep_verified_deleted"]:
        fails.append("G1 verified must-keep tests deleted")
    if s["f1"] < 0.65:
        fails.append("G4 f1 below 0.65")
    if abs(s["delete_rate"] - s["ref_delete_rate"]) > 0.15:
        fails.append("G4 delete rate more than 15 points from the reference")
    if s["review_rate"] > 0.15:
        fails.append("G4 review rate above 15%")
    print("PASS" if not fails else "FAIL: " + ", ".join(fails))


if __name__ == "__main__":
    main()
