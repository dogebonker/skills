#!/usr/bin/env python3
"""Score a use-patterns report against an answer key.

    python3 -I evals/score.py <report.md> [--key evals/expected.md] [--json]

The key's scoring rules are applied where they are mechanical:
- A finding matches a P or A row when its Where shares a file basename with any
  listed location of the row, the line ranges overlap within 2 lines, and its
  id matches the row's id or an "also accept" id, or failing that its family
  matches the row's family. A finding credits every row it matches by id, else
  the nearest row it matches by family. Several findings on one row count once.
- Confidence low (WEAK) scores half, unless the row's verdict says "WEAK accepted".
- A finding that matches no P or A row is a false positive, unless it sits on a
  "Not penalised" location or is a WEAK note on a decoy (neither way).
- A decoy whose location a "Considered and rejected" line names is rejected.
Fix direction is a judgment: matched pairs are printed under "Check fix
direction" for a human to tick, and the headline numbers assume they pass.
"""
import argparse
import json
import os
import re
import sys

EXT = r"(?:js|mjs|cjs|jsx|ts|tsx|mts|cts|go|rs|kt|kts|swift|py)"
REF = re.compile(r"([\w.-]+\.%s):(\d+)(?:-(\d+))?((?:,\s*\d+(?:-\d+)?(?=\s*(?:[,;)\]]|$)))*)" % EXT)
WORD = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
FAMILIES = {"gof", "dry", "kiss", "solid"}
TOL = 2


def refs(text):
    out = []
    for m in REF.finditer(text):
        name, a, b, more = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        out.append((name, a, int(b) if b else a))
        for extra in re.findall(r"(\d+)(?:-(\d+))?", more):
            out.append((name, int(extra[0]), int(extra[1]) if extra[1] else int(extra[0])))
    return out


def gap(r, s):
    """Lines between two refs: 0 when they overlap, None for another file or beyond TOL."""
    if r[0] != s[0]:
        return None
    d = max(r[1] - s[2], s[1] - r[2], 0)
    return d if d <= TOL else None


def nearest(locs, rows):
    """Rows whose Where overlaps locs, with the smallest gap."""
    best = {}
    for row in rows:
        ds = [d for r in locs for s in row["where"] if (d := gap(r, s)) is not None]
        if ds:
            best[row["id"]] = min(ds)
    low = min(best.values(), default=0)
    return {i: d for i, d in best.items() if d == low}


def cells(line):
    parts = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())]
    return parts[1:-1] if len(parts) > 2 else parts


def tables(lines):
    """Yield (heading, header, rows) for every Markdown table, with the nearest ## heading."""
    heading, i = "", 0
    while i < len(lines):
        if lines[i].startswith("## "):
            heading = lines[i][3:].strip()
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = []
            for c in cells(lines[i]):
                c = c.lower()
                header.append(c if c not in header else c + "#2")
            rows, i = [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(dict(zip(header, cells(lines[i]))))
                i += 1
            yield heading, header, rows
            continue
        i += 1


def parse_key(text):
    lines = text.splitlines()
    langs, rows, spared = [], [], []
    for heading, header, trs in tables(lines):
        if not {"id", "id#2", "kind", "where"} <= set(header):
            continue
        lang = heading.split(" (")[0].strip()
        langs.append(lang)
        for tr in trs:
            code, idcell = tr["id"], tr["id#2"]
            primary, _, rest = idcell.partition("(")
            also = set()
            if "also accept" in rest:
                also = {w for w in WORD.findall(rest.split("also accept", 1)[1].lower())
                        if w not in FAMILIES | {"or", "also", "accept"}}
            verdict = tr.get("expected verdict", "")
            rows.append({
                "id": code, "lang": lang, "family": tr.get("family", "").lower(), "kind": tr.get("kind", "").upper(),
                "ids": set(WORD.findall(primary.lower())) | also, "where": refs(tr.get("where", "")),
                "where_text": tr.get("where", ""), "fix": tr.get("expected fix", ""),
                "weak_full": "weak accepted" in verdict.lower(),
            })
    section = None
    for line in lines:
        if line.startswith("## "):
            section = line[3:].split(" (")[0].strip()
        if line.lower().startswith("not penalised") and section:
            spared.extend((section, r) for r in refs(line))
    return langs, rows, spared


def parse_report(text):
    lines = text.splitlines()
    findings = []
    for heading, header, trs in tables(lines):
        if not {"#", "family", "where"} <= set(header):
            continue
        scope = heading.split(":", 1)[1].strip() if ":" in heading else heading
        for tr in trs:
            conf = tr.get("confidence", "").lower()
            findings.append({
                "scope": scope, "code": tr.get("#", ""), "family": tr.get("family", "").strip().lower(),
                "ids": set(WORD.findall(tr.get("id", "").lower())),
                "where": refs(tr.get("where", "")), "where_text": tr.get("where", ""),
                "fix": tr.get("recommended fix", ""), "weak": "low" in conf or "weak" in conf,
            })
    rejected, inside = [], False
    for line in lines:
        if line.startswith("#"):
            inside = "considered and rejected" in line.lower()
        elif inside and line.lstrip().startswith("- "):
            item = line.strip()[2:]
            head = item.split(": ", 1)[0]
            rejected.append({"text": item, "where": refs(head) or refs(item)})
    return findings, rejected


def score(key_text, report_text):
    langs, rows, spared = parse_key(key_text)
    findings, rejected = parse_report(report_text)
    pa = [r for r in rows if r["kind"] in ("P", "A")]
    decoys = [r for r in rows if r["kind"] == "D"]
    by_id = {r["id"]: r for r in rows}
    lang_of = {loc[0]: r["lang"] for r in rows for loc in r["where"]}
    lang_of.update({loc[0]: lang for lang, loc in spared})

    credit, pairs, outcome = {}, [], []
    for f in findings:
        hit_id = nearest(f["where"], [r for r in pa if f["ids"] & r["ids"]])
        hit_fam = nearest(f["where"], [r for r in pa if f["family"] == r["family"]])
        cands = nearest(f["where"], pa)
        dec = nearest(f["where"], decoys)
        hits = hit_id or hit_fam
        # a decoy strictly nearer than every matching row takes the finding
        chosen = (list(hit_id) or list(hit_fam)[:1]) if min(hits.values(), default=TOL + 1) <= min(dec.values(), default=TOL) else []
        lang = next((lang_of[l[0]] for l in f["where"] if l[0] in lang_of), "unknown")
        label = f"{f['scope']} {f['code']} ({f['where_text']})"
        if chosen:
            for i in chosen:
                got = 0.5 if f["weak"] and not by_id[i]["weak_full"] else 1.0
                dup = i in credit
                credit[i] = max(credit.get(i, 0), got)
                pairs.append({"row": i, "finding": label, "by": "id" if hit_id else "family", "credit": got,
                              "duplicate": dup, "expected_fix": by_id[i]["fix"], "report_fix": f["fix"]})
            continue
        if any(lang == lg and gap(r, s) is not None for lg, s in spared for r in f["where"]):
            outcome.append((lang, "neutral", f"{label}: on a Not penalised location"))
        elif dec and f["weak"]:
            outcome.append((lang, "neutral", f"{label}: WEAK note on decoy {', '.join(dec)}"))
        elif dec:
            outcome.append((lang, "fp", f"{label}: decoy {', '.join(dec)} reported as a finding", dec))
        elif cands:
            outcome.append((lang, "fp", f"{label}: inside {', '.join(cands)} but family and id differ"))
        else:
            outcome.append((lang, "fp", f"{label}: matches no row"))

    reported = {d for o in outcome if o[1] == "fp" and len(o) > 3 for d in o[3]}
    rejected_ok, rejected_rows = set(), {}
    for item in rejected:
        for i in nearest(item["where"], decoys + pa):
            rejected_rows.setdefault(i, item["text"])
            if by_id[i]["kind"] == "D":
                rejected_ok.add(i)

    result = {"assumes_fix_direction": True, "languages": {}, "check_fix_direction": pairs}
    for lang in langs + (["unknown"] if any(o[0] == "unknown" for o in outcome) else []):
        mine = [r for r in pa if r["lang"] == lang]
        found = sum(credit.get(r["id"], 0) for r in mine)
        missed = [{"row": r["id"], "where": r["where_text"],
                   "rejected_in_report": rejected_rows.get(r["id"])} for r in mine if r["id"] not in credit]
        half = [r["id"] for r in mine if credit.get(r["id"]) == 0.5]
        ds = [r for r in decoys if r["lang"] == lang]
        result["languages"][lang] = {
            "recall": {"found": found, "total": len(mine)}, "half_credit": half, "missed": missed,
            "false_positives": [o[2] for o in outcome if o[0] == lang and o[1] == "fp"],
            "neutral": [o[2] for o in outcome if o[0] == lang and o[1] == "neutral"],
            "decoys": {"total": len(ds),
                       "rejected": [d["id"] for d in ds if d["id"] in rejected_ok and d["id"] not in reported],
                       "reported": [d["id"] for d in ds if d["id"] in reported],
                       "silent": [d["id"] for d in ds if d["id"] not in rejected_ok and d["id"] not in reported]},
        }
    L = result["languages"].values()
    result["total"] = {
        "recall": {"found": sum(v["recall"]["found"] for v in L), "total": sum(v["recall"]["total"] for v in L)},
        "false_positives": sum(len(v["false_positives"]) for v in L),
        "decoys": {k: sum(len(v["decoys"][k]) for v in L) for k in ("rejected", "reported", "silent")}
        | {"total": sum(v["decoys"]["total"] for v in L)},
    }
    return result


def pct(found, total):
    return f"{found:g}/{total} ({100 * found / total:.1f}%)" if total else "0/0"


def render(res, report, key):
    out = [f"Report: {report}", f"Key: {key}",
           "Headline numbers assume every matched pair's fix is in the expected direction (see Check fix direction).", ""]
    for lang, v in res["languages"].items():
        d = v["decoys"]
        out.append(f"{lang}: recall {pct(v['recall']['found'], v['recall']['total'])}, "
                   f"false positives {len(v['false_positives'])}, decoys rejected {len(d['rejected'])}/{d['total']}, "
                   f"silent {len(d['silent'])}" + (f" ({', '.join(d['silent'])})" if d["silent"] else ""))
        for m in v["missed"]:
            why = f"; under Considered and rejected: {m['rejected_in_report']}" if m["rejected_in_report"] else ""
            out.append(f"  missed {m['row']} ({m['where']}){why}")
        out += [f"  half credit (WEAK) {i}" for i in v["half_credit"]]
        out += [f"  false positive: {x}" for x in v["false_positives"]]
        out += [f"  neutral: {x}" for x in v["neutral"]]
    t = res["total"]
    out += ["", f"Total: recall {pct(t['recall']['found'], t['recall']['total'])}, false positives {t['false_positives']}, "
            f"decoys rejected {t['decoys']['rejected']}/{t['decoys']['total']}, silent {t['decoys']['silent']}, "
            f"reported as findings {t['decoys']['reported']}", "", "## Check fix direction", ""]
    for p in res["check_fix_direction"]:
        tag = f"matched by {p['by']}" + (", half credit" if p["credit"] == 0.5 else "") + (", duplicate" if p["duplicate"] else "")
        out += [f"[ ] {p['row']} <- {p['finding']} [{tag}]", f"    expected: {p['expected_fix']}",
                f"    report:   {p['report_fix']}", ""]
    return "\n".join(out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("report")
    ap.add_argument("--key", default=os.path.join(here, "expected.md"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.key, encoding="utf-8") as k, open(a.report, encoding="utf-8") as r:
        res = score(k.read(), r.read())
    if not res["languages"]:
        sys.exit(f"no answer-key tables found in {a.key}")
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print(render(res, a.report, a.key))


if __name__ == "__main__":
    main()
