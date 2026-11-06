# Evals

## t3code replay

`t3code/` replays pingdotgg/t3code PR #22557 on the tree just before it (`c3540a7854`) and scores the decisions against `settled`: what main looked like on 2026-10-23 (`c58d558e10`), after the snap, the second-pass prunes, #24058 and the four restore PRs. The snap's own labels are kept as `label` (`--ref label`).

| File | What it is |
|---|---|
| `build_key.py` | Inventories the pre-snap, post-snap and settled trees, labels every pre-snap test, draws the samples, writes `key.jsonl` and `sample*.txt` |
| `must-keep.json` | Tests the team restored after the snap. `verified` entries were each justified in a restore PR. `COLLATERAL` entries came back only because a file was restored verbatim. `UNVERIFIED` entries are likely members of the 22 auth tests restored in review of #22557 (exact titles were never published) |
| `must-keep-fresh.json` | Three tests PR #24058's review restored after its own over-cut. Kept out of every sample, used as a blind G1 check |
| `score.py` | Precision, recall and F1 of `delete` against the reference, delete rate, must-keep losses. `review` counts as not deleted |

Splits (by file): `train` (102 files) and `holdout` (99) form `dev`, used for tuning. `test` (102) was first scored at round 10 and never tuned on. `test2` (102) was drawn after that and scored only with the final code.

### Gates

- G1: no verified must-keep test deleted, on dev and on the fresh set.
- G2: no corrupted file after apply (see the user-repo runs).
- G3: no new test failure after apply (see the user-repo runs).
- G4: on a blind split, F1 at least 0.65 against `settled`, and a delete rate within 15 points of the reference.

### Run

```sh
git clone https://github.com/pingdotgg/t3code.git && git -C t3code checkout c3540a7854   # full history: guard uses git log -S
python3 -I evals/t3code/build_key.py t3code
# inventory of the splits to run (here train + holdout = dev)
python3 -I -c "import json,sys; ids={r['id'] for r in map(json.loads,open('evals/t3code/key.jsonl')) if r['split'] in sys.argv[1:]}; [print(l,end='') for l in open('evals/t3code/inventory.pre.jsonl') if json.loads(l)['id'] in ids]" train holdout > inv.jsonl
python3 -I scripts/classify.py inv.jsonl --repo t3code -o dec.jsonl --passes 2 --double-fraction 0.5 --cache cache
python3 -I scripts/guard.py evals/t3code/inventory.pre.jsonl dec.jsonl --repo t3code -o guard.jsonl
python3 -I scripts/review.py evals/t3code/inventory.pre.jsonl guard.jsonl --repo t3code -o final.jsonl --cache cache
python3 -I evals/t3code/score.py final.jsonl --split dev
```

A dev run costs about $9 (classify $1, review $8). Haiku output varies, so F1 moves by about 0.02 between identical runs.

### Results

| Round | Change | Dev F1 | Dev delete rate (ref 54%) | G1 dev (17) | G1 fresh (3) |
|---|---|---|---|---|---|
| 0 | first rubric, "keep when unsure" | 0.10 (vs `label`, train only) | 2% | 0 lost | not run |
| 2 | delete unless a Keep category fits, Sonnet reviewer | 0.65 holdout raw, 0.60 after review | 50% | 9 lost | not run |
| 5 | fix-commit tests always kept, cover required | 0.51 | 30% | 2 lost | 0 lost |
| 7 | security words kept, quoted cover proof | 0.36 | 20% | 0 lost | 0 lost |
| 8 | reviewer keeps only security, negative, contract, fix edges | 0.61 | 43% | 0 lost | 0 lost |
| 10 | one test per behavior, proof only where a behavior can vanish | 0.64 | 44% | 0 lost | 0 lost |
| 11 | round 10 with an Opus reviewer | 0.61 | 41% | 0 lost | 0 lost |
| final | round 10 plus review fixes from the verifier pass: cover quotes must sit inside a surviving test, reviewer prompt without the keyword lists | 0.66 | 46% | 0 lost | 0 lost |

The final row is the shipped config. On the unseen splits:

| Split | Tests | F1 | Precision | Recall | Delete rate (ref) | G4 |
|---|---|---|---|---|---|---|
| test | 1,606 | 0.634 | 0.70 | 0.58 | 41.5% (49.6%) | F1 misses |
| test2 | 946 | 0.669 | 0.71 | 0.63 | 49.6% (55.4%) | passes |
| both | 2,552 | 0.648 | 0.70 | 0.60 | 44.5% (51.7%) | at the line |

G1 holds on every run: no verified must-keep deleted on dev (17) or in the fresh set (3). G4 sits at the 0.65 floor: the delete-rate check passes everywhere, and F1 passes on one unseen split and misses on the other.

What limits F1: the team's own labels disagree with each other on similar files. Most errors sit in a few large UI-logic files (`Sidebar.logic.test.ts`, `rightPanelStore.test.ts`, `session-logic.test.ts`) where the team kept some view-logic tests and cut near-identical ones elsewhere. Two Haiku passes on the same file agree on 88% of tests, which caps agreement with any single labeling run. Every change that raised F1 past 0.65 deleted restored must-keep tests again.

## User repos

The full pipeline ran on local clones of seven repos (round-10 config for the first six, final config for E), followed by each repo's own typecheck, lint and test suite. G2 and G3 pass on all seven. Private repos are labelled A to E.

| Repo | Language | Tests (units) | Deleted | Checks after apply | Failing before → after | New failures | Suite time | Model cost |
|---|---|---|---|---|---|---|---|---|
| A (private) | TS | 900 | 447 | tsc | 3 → 3 | 0 | 196s → 187s | $3.0 |
| B (private) | TS | 2,205 | 1,211 | tsc, lint (one error also failing at baseline) | 0 → 0 | 0 | 53s → 40s | $7.5 |
| plumb | Python | 537 | 155 | py_compile | 2 → 1 (a failing test was deleted) | 0 | 282s → 214s | $1.2 |
| C (private) | Python | 239 | 78 | ruff | 0 → 0 | 0 | 14s → 8s | $0.6 |
| D (private) | Python | 5,706 | 1,986 | ruff, mypy --strict, basedpyright | 0 → 0 | 0 | 477s → 305s | $15.7 |
| archgraph | Rust | 1,093 | 317 | cargo fmt, clippy -D warnings | 0 → 0 | 0 | 118s → 123s | $4.1 |
| E (private) | Go, TS | 4,470 | 2,007 | go vet, golangci-lint, tsc (after removing dead helpers) | 0 → 0 | 0 | Go 99s → 65s, vitest 31s → 26s, node 13s → 7s | $26 |

Timings ran next to the model calls and are noisy. archgraph's suite is dominated by fixed setup, so cutting tests did not change it.

Three deleted tests had to come back as step-7 fallout, all hidden coupling no static check sees: a test in B whose cleanup call left state the next test relied on, a test in D holding the module's only `.dispose()` call that a convention test requires, and a test in E whose mock return values the next test in the file relied on (`vi.restoreAllMocks` does not reset `vi.fn` implementations). The runs also found and fixed ten script bugs (bun, unittest, node TAP and turbo output parsing, Rust unused imports, `Cargo.lock` rewrites, import sorting after removal, resolved review rows missing from the report, and two Go bugs below), each with a unit test.

E, the only Go repo, found two Go bugs:
- A `TestX` with `t.Run` subtests was judged apart from them. The reviewer deleted every subtest as "covered by the parent" and left the parent running setup only, and a deleted parent took its kept subtests with it. Access-control subtests went both ways (a denied non-member, rejections across tenant scopes). Now a Go function or `t.Run` with literal-named subtests is a container, like `describe`: only leaves are judged and deleting the last one raises `empties`. An emptied parent is removed only when nothing but its subtests and comments is left. One with code of its own (setup, a helper check, a `t.Run(tc.name, ...)` table) keeps that code, and apply lists it for step 6.
- Deleting a subtest left the parent's locals unused (`c, srv := newClient(t)` with `srv` used only in the subtest), a compile error, so apply reverted whole files (98 deletes in 6 files). Apply now renames such a local to `_` and re-runs `go vet`. Other shapes (a redeclared `err`, `switch x :=`, `else if x :=`, `case v := <-ch`, a second `:=` on the line, a name assigned again later) still revert the file.

The E row comes from the run before the last refinement (emptied parents with code of their own are kept). It does not change that run: the one Go parent it emptied held only its two subtests.

On E, step 6 cleanup took an agent: `tsc` (noUnusedLocals) and golangci-lint (`unused`, `unparam`) flagged about 100 dead test helpers the deleted tests left behind. Main was clean on both, and the cleanup touched test files only.
