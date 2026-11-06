---
name: test-snap
description: "Deletes low-signal tests in bulk so CI runs faster and flakes less, using the method of t3code PR #22557 (11k of 26k tests cut): a Haiku swarm judges every test against one rubric, mechanical guards and a Sonnet reviewer protect the last test of each behavior, deletions apply by AST range, before/after timing proves the win. TS/JS, Python, Rust, Go. Use when the user asks to prune, snap, cut or slim a test suite, says CI is slow or flaky because of too many tests, or asks which tests are low-value."
---

Cut the tests that cost CI time and give no signal, and keep every test that is the last guard of a behavior. The PR this copies over-deleted 29 tests that each were the only guard of a behavior, and restored them in four follow-up PRs. The guards and the review step exist to avoid repeating that. `references/decisions.md` holds the full method (D1 to D22) with evidence. Read it when a step below names a decision.

Scripts are in `scripts/`. Run them with `python3 -I`. Each takes `--help`. They need `uvx` (fetches ast-grep) and the `claude` CLI on PATH. On t3code the model calls cost about $4 per 1,000 tests (classify about $0.5, review the rest). Results are cached by prompt and file content, so re-runs cost nothing.

## 1. Baseline

Work in a throwaway `git worktree` on a new branch. Find the repo's test command from its config (`package.json` scripts, `pyproject.toml`, `Cargo.toml`, `go.mod`, CI workflow). Run it with `scripts/measure.py --repo <wt> --cmd "<cmd>" -o before.json`. Tests that already fail here are pre-existing and never block the snap (D14).

Done when `before.json` exists and you can name each pre-existing failure.

## 2. Inventory

`scripts/inventory.py <wt> -o inventory.jsonl`. Pass `--paths` globs to skip vendored code, generated code and fixtures (t3code keeps vendored repos in `.repos/` that would double the count). Parse warnings drop only the tests that overlap a parse error.

Done when the count per top-level directory looks right against the repo's test files.

## 3. Classify

`scripts/classify.py inventory.jsonl --repo <wt> -o decisions.jsonl --passes 2 --double-fraction 0.5 --budget-usd <cap>`. Haiku judges each file against `references/rubric.md` (D2, D3, D5). It keeps a test only when it fits a Keep category, and keeps only the single strongest test of each behavior. Files picked for the double pass delete a test only when two calls agree, with a third call breaking ties (D6, D7). Set the cap from the test count before starting. Calls already in flight finish after the cap is reached, so the total can pass it by a few calls.

Done when every inventoried test has a row and `not-judged` / `classifier-error` rows are zero or explained.

## 4. Guard

`scripts/guard.py inventory.jsonl decisions.jsonl --repo <wt> -o decisions.guarded.jsonl`. Run it against the full inventory even when you classified a subset. For each delete:
- a hard sensitive word in the path or title (secret, permission, token, scope, migration, timezone, the list in `references/rubric.md`) keeps the test without review (D12),
- a soft sensitive word, being the sole test of a production symbol, emptying its file or describe block, or having been added by a fix commit sends it to `review` (D4, D18).

## 5. Review

`scripts/review.py inventory.jsonl decisions.guarded.jsonl --repo <wt> -o decisions.final.jsonl --budget-usd <cap>`. Sonnet reads each flagged test with read-only access to the repo and keeps it only when it is the last check of a security or data property, a negative property, an external contract, or the edge a bug fix changed. A delete of a fix-commit test, or of the last test of a symbol that also empties its file, must quote a line from a surviving covering test. The script checks the quote against that file and turns an unproven delete into keep.

Then read the review rows yourself: every row still `review` (budget or error), and a sample of 10 deletes and 10 keeps. When you keep a test that looks vacuous, mutate the guarded line and confirm the test fails (D18 found three restored tests that passed with the guard removed).

Done when no row has verdict `review` and the sampled verdicts hold up.

## 6. Apply

`scripts/apply.py inventory.jsonl decisions.final.jsonl --repo <wt> --check > apply.txt`. It deletes by byte range from the AST, removes emptied containers and files, removes unused imports (biome, ruff, goimports), and reverts any file that stops parsing or, for Go (and Rust with `--check`), stops compiling (D8). Then clean up what the deleted tests alone used (D9): run the repo's dead-code tool if it has one (`knip`, `vulture`, `cargo machete`, `deadcode`), drop fixtures and helpers nothing imports, empty `test` scripts and dev dependencies only tests used. `apply.txt` lists Go test functions emptied of subtests but kept for code of their own: delete the ones left with setup only, keep the ones that still check something. Keep production behavior unchanged. Typecheck, lint and build must pass.

## 7. Measure and fix fallout

`scripts/measure.py --repo <wt> --cmd "<cmd>" -o after.json`, then `scripts/measure.py compare before.json after.json`. A new failure means the snap broke something test infrastructure relied on (D15: shard weights, bundler pre-scan of a dependency, a shared setup file). Fix the infrastructure. When a deleted test turns out to be load-bearing for another test, restore that test.

Done when compare shows no new failures and the time saved is a number.

## 8. Report

`scripts/report.py --inventory inventory.jsonl --decisions decisions.final.jsonl --apply apply.txt --before before.json --after after.json` writes `test-snap-report.md`: counts by verdict, category and package, every review decision with its reason, and the before/after table. Use it for the PR body. Offer the regrowth guards from D20 to D22 (a lint rule against wall-clock waits in tests, a testing doc the review bot checks new tests against) as a follow-up, not part of this change.

## Evals

`evals/t3code/` replays the PR on stratified samples of t3code before the snap and scores the result against what the t3 team settled on after its follow-up prunes and restores. `evals/README.md` has the run steps, the gates and the last scores.
