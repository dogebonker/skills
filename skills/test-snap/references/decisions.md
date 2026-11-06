# Test snap method, split into decisions

Source: pingdotgg/t3code PR #22557 (merged 2026-10-21, merge commit 05696c6, parent c3540a7) and the PRs that followed it. All quotes are from PR bodies. The #22557 body is the only record of the first-pass rubric text. The swarm prompt, the per-file inventories (`mobile.tsv`, `desktop.tsv`, `server-rest.tsv`) and the 22 restored auth tests are not published in the repo or in any review comment. Items I could not verify are marked.

## D1. Goal and metric

Decision: Optimize for CI wall time and flake rate, not for coverage or test count.

Bought: 25,928 to 14,847 tests (about 43% removed), 456 test files deleted outright, 1,195 trimmed, summed test-file time 1,205s to 490s (-59%). Server 1,040s to 564s, web 132s to 53s, desktop 20s to 5s.

Evidence: #22557 "Release runs fail most of the time on flaky browser tests, and a lot of tests check things types already guarantee, mirror the code, or wait on real timers." #22562 gives the flake baseline: "main was red in ~600 of ~2,900 runs since September".

Failure or guard: Count was the headline number, but the real signal was time and red runs. Later growth tracking (#26166) switched back to count: "9,316 to 10,991 in five days, about 335 a day".

## D2. Delete rubric

Decision: Define deletable tests by named classes, not by a score.

Bought: A rubric a cheap model can apply per file. Classes: type-redundant, trivial logic, basic DOM behavior, real or fake timers, mock-call mirrors, smoke tests, duplicate table cases, wall-clock perf asserts.

Evidence: #22557 "Delete: type-redundant, trivial logic, basic DOM behavior, real or fake timers, mock-call mirrors, smoke tests, duplicate table cases, and wall-clock perf asserts."

Second-pass PRs add finer classes: constant and literal mirrors, mocked call-sequence mirrors, error tag or message wording, log wording, copy text, sibling cases that differ by one literal, lookup-table enumeration, heuristic-parser table bloat, cases subsumed by a sibling (#22588, #22589, #22591, #22592, #22593, #22599).

Failure or guard: "Real or fake timers" and "basic DOM behavior" were the classes that over-matched. The 22 auth tests cut as "timing" (D12) and the DST scheduling tests (D18) plausibly fell under the same class (inference, the PRs do not say).

## D3. Keep rubric

Decision: Write an explicit keep list next to the delete list and let keep win ties.

Bought: Protects the categories where a silent regression is expensive.

Evidence: #22557 "Keep: orchestration and event-sourcing correctness, provider protocol translation, auth and permission guards, persistence and migrations, external-format parsing, and deterministic race fixes." The same list was later copied into docs/internals/testing.md under "What to test" (D19).

Failure or guard: The keep list named auth guards, yet 22 auth tests were still deleted by the swarm. The list did not stop the labeling error, review did (D12).

## D4. Regression rule using git history (second pass)

Decision: Any test whose adding commit is a `fix(...)` stays, and gets a `// regression: #NNNN <fix subject>` comment when the title does not name the bug.

Bought: A mechanical, non-LLM keep signal. Mobile annotated 27 regression tests, server 33, web about 110 kept cases plus new annotations, orchestration-v2 kept about 60 named fix tests.

Evidence: #22591 "Every listed case was checked with `git log -S"<title>"`, including the history before a rename". #22599 "Any listed test whose adding commit is a `fix(...)` stayed."

Failure or guard: The first pass (#22557) has no record of using this rule. The DST tests restored in D18 came from fix #15768. Applying the git-history rule in the first pass would likely have protected at least that one. This is inference, not stated by the authors.

## D5. Model choice: a Haiku swarm, Opus as the orchestrator

Decision: Use many cheap model agents to classify, one stronger model to design the pipeline and apply it.

Bought: Whole-repo classification of about 1,650 test files in one session.

Evidence: #22557 "A swarm of Claude Haiku 5.5 agents read every test file against one rubric." Footer: "Created with Claude Opus 5.5 (test selection by Claude Haiku 5.5) in Claude Code."

Failure or guard: The cheap model mislabeled auth tests as "timing" (D12). In #26166 the authors found a similar tier effect for the review bot: "GPT-6 Luna is too weak for this check at any length. It flags good bug-fix tests on every prompt tried."

## D6. Two independent passes with a third tiebreak vote

Decision: On about half the files, run two independent classification passes, delete only on agreement, and settle disagreements with a third vote.

Bought: A conservative bias on the files that got it. About 987 files got two passes. About 1,900 test-level disagreements were settled by a third Haiku vote.

Evidence: #22557 "There a test is deleted only when both agree, and a third Haiku vote settled the ~1,900 disagreements."

Failure or guard: A third vote from the same model family does not fix a shared misreading. The 22 auth mislabels survived into the PR, so consensus among Haiku votes did not catch them. I could not verify whether the 22 came from single-pass or two-pass files.

## D7. Single pass for the other half

Decision: Do not double-run every file. Files outside the two-pass half got one pass.

Bought: Roughly halves classification cost.

Evidence: #22557 "The other files got one pass." No selection criterion for which half got two passes is stated. I could not verify one.

Failure or guard: Single-pass files had no consensus guard. This is the likely home of the 4 later-restored sole-coverage tests, but the restore PRs do not say which pass produced each cut.

## D8. Apply deletions with the AST, matched by test title

Decision: The model outputs test titles. A script deletes them with the TypeScript AST, then removes unused imports and helpers the same way.

Bought: No hand edits across 1,651 files, and a repeatable, reviewable diff. The 258,735 deleted lines include dead imports and helpers.

Evidence: #22557 "Deletions are applied with the TypeScript AST, matched by test title, not by hand. Imports and helpers left unused afterwards are removed the same way."

Failure or guard: Title matching is exact only when titles are unique within a file. Template titles (`$zone`, `%s`) and `.each` tables mean one title can delete a whole table. #22588 and #22593 later thinned tables row by row instead.

## D9. Cascade cleanup after deleting tests

Decision: Treat each deletion as the start of a cleanup chain and run the repo's dead-code tools until clean.

Bought: No orphaned production code. About 420 exports un-exported, about 48 never-called declarations deleted, one source file (`builtInProviderAdapterDrivers.ts`) deleted with its doc updated, orphan fixtures deleted, two empty `test` scripts removed, unused dev deps dropped, `test:perf:v2-wire` list, mobile react-test list, and knip entries updated.

Evidence: #22557 "knip `--exports` failed on ~420 exports that only deleted tests used. Those are un-exported now, and ~48 declarations nothing calls are deleted, so there is no production behavior change."

Failure or guard: Stale references still leaked. #28800 found two files missing from the mobile `reactTests` list after later deletions, and #28746 found four dead keys in `shardWeights.json`. The cascade is not done once, it has to be rerun after every deletion PR.

## D10. Keep-on-purpose list for guards that look low-signal

Decision: Name a short list of tests that look like deletion candidates but are kept, with the reason written in the PR.

Bought: Protects perf and dependency guards that a rubric would delete.

Evidence: #22557 "Kept on purpose: both `reactCompilerCoverage.test.ts` files (documented perf guard), and slimmed copies of `bundledDev.test.ts` and `fileEditorVirtualization.test.ts`".

Failure or guard: #22591 repeated the pattern, keeping a test because `docs/internals/web-ui.md` names it, and #22589 kept a test because "Deleting it would leave dead product code that knip flags". Documentation pointing at a test is a keep signal.

## D11. Human or stronger-model review of the diff

Decision: Review the diff with a second model family and a human before merge.

Bought: Caught the auth over-deletion (D12). Also caught a stale `mermaid` import breaking main.

Evidence: #22557 "Reviewed with sol-loop: 2 rounds with GPT-6.1 Sol. Sol verdict: approved." Macroscope flagged it for human approval: "removes authentication-related coverage, so the sensitive-area criteria require human review."

Failure or guard: The PR has no inline review comments and no review objects in the API. The restore of the 22 tests is described only in the body, so I could not tell whether Sol, Macroscope, or a human found them.

## D12. Restore auth tests mislabeled as timing

Decision: Put back 22 auth boundary tests the swarm had cut as "timing", because they use the deterministic Effect clock.

Bought: Kept session and websocket credential expiry, desktop bootstrap expiry and rotation, MCP credential liveness and thread isolation, the one-scope-per-RPC guard, and scope-narrowing checks.

Evidence: #22557 "Review restored 22 auth boundary tests the swarm had cut as "timing" (they use the deterministic Effect clock)".

Failure or guard: The swarm treated any `TestClock`, `Clock`, or `sleep` as a real or fake timer. Rule for a skill: a test that advances a deterministic clock to prove a security deadline is a keep, not a timer test. Exact titles are not published. `evals/t3code/must-keep.json` lists candidates that survive in the merged tree (unverified).

## D13. Measure before and after with the same command and machine

Decision: Run the same test command on the same machine before and after, with the vitest JSON reporter, and report per package.

Bought: A table that others can check: tests, wall time, and summed file time per package.

Evidence: #22557 "Local before/after, same commands and machine (vitest JSON reporter)".

Failure or guard: Local timings are single runs. Wall time per package, not CI time, is reported. The title claim "CI runs faster and flakes less" has no CI-side before and after in the PR. #30866 (open) later re-times server shards from CI.

## D14. Check remaining failures against main

Decision: Run the suite after the change and confirm each remaining failure also fails on main.

Bought: Separated pre-existing failures from regressions without fixing unrelated tests in a deletion PR.

Evidence: #22557 "The server failures that remain locally (`pinnedRuntime`, `ServerEnvironment`, `ProviderInstanceRegistry`, `AcpSessionRuntime.processTree`) fail the same way on `main` on this machine."

Failure or guard: Also noted `TelemetryExportSettings` "timed out once under load" and declared it untouched. A flake was explained by load, not rerun until green.

## D15. Infra fallout: shard weights and Vite prebundle

Decision: Update test infrastructure that depends on test count and timing in the same PR.

Bought: Balanced server shards and a working browser test run.

Evidence: #22557 "`shardWeights.json` drops deleted files and scales trimmed ones by their measured speedup, so server shards stay balanced." And "With fewer tests, Vite's dependency scan no longer found it and reloaded mid-run, which broke a test iframe."

Failure or guard: Deleting tests changed Vite's dependency discovery. The fix was to pre-bundle `@base-ui/react/autocomplete` explicitly. Deleting tests can remove incidental warmup that other tests relied on.

## D16. Second-pass prunes by area, against a reviewed inventory

Decision: After the big merge, prune each area in its own PR from a reviewed inventory (TSV of delete, trim, keep per test), with counts and a kept-list in each body.

Bought, per PR: mobile 1,107 to 1,017 test cases (-90, -1,918 lines, #22588). Desktop 781 to 695 (-86, #22589). Web 1,840 to 1,494 in touched files (-346, #22591). Server 1,019 to 910 (-108, #22592). Packages about -107 declarations and about 490 table rows (#22593). orchestration-v2 1,183 to 1,022 (-161, -11,367 lines, #22599). Sum of declarations is about 900.

Evidence: #22588 "Second-pass prune of `apps/mobile/**` tests against the reviewed inventory (`mobile.tsv`: 9 deletes, 69 trims)."

Failure or guard: The second pass is mostly trims (thin `.each` tables to 2 to 4 rows, keep the row that pins a fix), not deletes. Floors were set per table: "(each keeps 2 to 4 representative rows)". Splitting by area kept each diff reviewable.

## D17. Prune again later, with a review that catches over-cuts

Decision: A later sweep (#24058) deletes low-value tests plus dead test-only exports, and is paired with a review that restores over-cuts in the same PR.

Bought: 126 test cases removed, 2,561 net lines. Dead exports verified caller-less by grep across the repo before deletion.

Evidence: #24058 "Review caught 9 cuts that went too deep, and they are restored in the second commit". Restored: checkpoint `diff.noprefix` guard (#9438), preview-tools allOf guard (#5128), `threadAccess` wiring case (#22452), timestamp rows (#20094), amount-regex branches (#21519), release-notes heading skip (#9138), `Ctrl++` row, multi-model send guard rows.

Failure or guard: Even a model-reviewed second sweep cut 9 guards. Most of the 9 had a fix PR number in their history, so D4 would have flagged them. Those 9 were never in the repo after merge (cut and restored in one PR), so they are not in the must-keep list.

## D18. Restores: the sole test of a behavior

Decision: Four small PRs restored 29 tests byte-identical to the pre-snap version, each with a mutation or recomputation check.

Bought: Brought back the only guard for four behaviors.

Evidence: #24058 "Four restore PRs (#23977, #23980, #23991, #24011) bring back 29 test cases the October snap over-deleted."

Common pattern: every restored test was the only test of its behavior, and every behavior was a security, correctness, or lifecycle contract that fails silently.
- #23991 (7 tests, `ScheduledTaskService.interval.test.ts`): DST handling for interval and fixed-time schedules. "Nothing on main checked either behavior after the deletion." Came from fix #15768.
- #24011 (16 tests, `ProjectSettingsPanel.browser.test.tsx`): permission recheck when access is revoked mid-update, after confirmation, or mid-edit. The surviving file "only covers removal planning copy".
- #23980 (5 tests, `copyTextWithHaptic.test.ts`): clipboard failure logs must not contain the copied secret. "the only test proving clipboard copy failures cannot log secrets". This is a negative-property test, so no happy-path test can substitute.
- #23977 (1 test, `renderScheduler.test.ts`): coalescing, cancellation, and disposal. "the only direct test for `createRenderScheduler`".

Failure or guard: Three of four were deleted whole-file or whole-describe, which the file-level rubric made easy. The #23980 file survived #22557 and was cut by second-pass #22588 under "Log or copy wording" (verified: the file exists at 05696c6 and is missing after #22588). The restore PR still calls it a snap deletion. The log-wording class over-matched a security property. The #24011 restore found that three restored tests were vacuous: "they could pass if the guard never ran". Mutation check: with the recheck short-circuited, exactly those three failed and the other 13 passed.

## D19. Bound the restores with an offsetting deletion

Decision: Ship a deletion PR bigger than the restores, and merge it first.

Bought: Net suite shrinks even while restoring.

Evidence: #24058 "The deal was: delete at least twice as many low-value tests first, so the suite does not just grow back." It reports 4.3x the restored case count.

Failure or guard: A negotiated ratio, not a rule from the snap itself. I could not verify it was applied to later restores.

## D20. Regrowth prevention: lint rules on time waits

Decision: Turn the flake causes into lint errors so new tests cannot reintroduce them. Five custom oxlint rules.

Bought: Named flakes removed and made unrepresentable. 33 wall-clock sites in 19 files (#22562), 31 files rewritten for real-clock waits (#22564), 16 browser files (#22561), 234 call sites converted to event-driven harness methods (#22565).

Evidence: #22562 "These rules make those tests fail lint instead of CI." Rules: `no-wall-clock-in-tests`, `no-real-time-wait-in-tests`, `no-frame-waits-in-browser-tests`, `no-polling-loop-in-tests`, `no-test-timeout-or-unreasoned-skip`.

Failure or guard: The polling rule shipped as warn and the warn only grew: #23983 "A warn that exits 0 only grows." It was flipped to error with a per-file burn-down list of 14 files and 25 hits, and fully enforced in #25120. Known gap: "the polling rule only sees waits written inline in the loop, not waits hidden behind a local helper." The real-time rule also had a silent exemption for all browser tests until #23983.

## D21. Regrowth prevention: a testing doc that is also the review standard

Decision: Write the rules in docs/internals/testing.md and AGENTS.md, and point the review bots at that file.

Bought: Authors, agents, and reviewers share one definition. The doc restates the keep list (D3) and adds "Extend before you add" and "Test at one layer".

Evidence: #24204 "CodeRabbit asks for tests that just repeat the implementation, like one assertion per label in a `switch`." Doc rule: "In review, ask for a missing test only when it would catch a real regression."

Failure or guard: Review bots had been asking for the low-signal tests the snap deleted. Without the doc pointer, the bot reintroduced them. #26166 found growth anyway: 335 tests per day, caused by accumulation (a new `it` per fix, the same case at several layers, copy text tests) and by Macroscope skipping tests entirely via `.macroscope/ignore.md`.

## D22. Regrowth prevention: a test-signal review check with its own eval

Decision: Add a review check that reads only added or grown tests, never asks for more coverage, and is tuned against a labeled eval.

Bought: Shortest prompt that held: an 88-word pointer to testing.md. The eval has 9 PR test diffs (5 low-signal, 4 good, including tests deleted in #22592). Final run: Terra 27/27 samples, Sol 18/18. Luna failed on good tests at every prompt length.

Evidence: #26166 "New eval `evals/test-signal/` runs the check body on 9 PR test diffs".

Failure or guard: The check is measured on 9 cases. Small sample. The eval still gives a regression test for the bot itself.

## Tools used

| Tool | Role | Evidence |
|---|---|---|
| Claude Haiku 5.5 swarm | Classify every test file against the rubric, vote | #22557 |
| Claude Opus 5.5 in Claude Code | Orchestrate, write scripts, author the PR | #22557 footer |
| TypeScript AST script | Delete tests by title, prune unused imports and helpers | #22557 |
| knip (`--exports`, `--include files`) | Find exports and files only deleted tests used | #22557, #22588, #22589, #22592 |
| vitest JSON reporter | Before and after counts and timings | #22557 |
| `git log -S"<title>"` | Find the adding commit, apply the fix-commit keep rule | #22591 |
| GPT-6.1 Sol (sol-loop) | Independent reviewer, 2 rounds, approved | #22557, #24058, restore PRs |
| Macroscope | Approvability gate, sent #22557 to human review for auth coverage | #22557 comments |
| Claude Opus 5.5 reviewer | Found the 9 over-cuts in #24058 and the vacuous tests in #24011 | #24058, #24011 |
| oxlint custom plugin `t3code/*` | Ban wall-clock, real-time waits, frame waits, polling, test timeouts | #22561, #22562, #22564, #22565, #23983, #25120 |
| CodeRabbit config | Review tests against docs/internals/testing.md | #24204 |
| Macroscope check `test-signal` | Review added tests only, with an eval | #26166 |
| Shard weights script | Rebalance CI shards after count change | #22557, #28746 |

## Failure modes observed

- F1. Clock-advancing auth tests labeled as timer tests. 22 restored in review (D12).
- F2. Whole-file deletions removed the only test of a behavior. Four restore PRs, 29 tests (D18).
- F3. Log-wording class matched a security property (secret redaction in logs). Restored in #23980.
- F4. Vacuous restored tests. Three revocation tests passed with the guard disabled. Fixed in #24011.
- F5. Sweeps with a model reviewer still cut guards. 9 over-cuts in #24058 (D17).
- F6. Consensus among same-family cheap-model votes did not catch a shared misreading (D6).
- F7. Deleting tests removed incidental Vite dependency warmup and broke a browser test iframe (D15).
- F8. Stale references to deleted files remained in shard weights and the mobile react-test list (#28746, #28800).
- F9. Test-only exports leaked into production code and failed knip, requiring un-export and dead code removal (D9).
- F10. Growth after the snap: about 335 tests per day, with 9,316 to 10,991 in five days (#26166).
- F11. A lint rule shipped as warn only grew (#23983). Real-time ban had a silent browser-test exemption.
- F12. Review bots requested the low-signal tests the snap removed (#24204).
- F13. The PR claims CI speed and flake gains, but the numbers are local single runs. No post-merge CI comparison appears in the PR.
- F14. Not found: no later issue or PR links a production regression to a deleted test. Searches for "test snap", "#22557", "snap deleted", "over-deleted", "deleted test" returned only the restore PRs and cleanup PRs. This does not prove none exist.
