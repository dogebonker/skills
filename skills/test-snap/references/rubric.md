# Rubric

The classifier reads this file as its instructions. Each test gets one verdict and one category.

The suite is too big and too slow. Your job is to cut it hard. A test stays only when it fits a Keep category below. Everything else is deleted. A separate guard step and a reviewer re-check every risky delete (security words, last test of a symbol, emptied files, tests added by bug fixes), so judge each test on its own signal and leave safety to them.

## How to judge a file

1. Group the listed tests by the behavior they exercise (usually the function, method or component under test).
2. In each group, keep only the single strongest test that fits a Keep category: the one that would catch the most plausible wrong change. Delete the rest of the group as `variant`, even when each variant checks a different branch or input.
3. Delete every test that fits a Delete category.

## Delete

| Category | Delete when the test |
|---|---|
| `variant` | is another case of a behavior a stronger test in the same file already covers: another input, another branch of a small function, another accept or reject case of the same validator, another row of a table, another platform of the same rule. |
| `ui-logic` | checks client UI logic: which control shows, labels and copy, layout and sizing, ordering, filtering, grouping or search of UI lists, selection and toggle state, collapsed or expanded state, view-model projections for display, client caches of display data, menu items, toolbar state. |
| `error-shape` | checks how an error is wrapped, named, logged or worded: error message text, cause chaining, detail fields, error tags. |
| `type-redundant` | checks something the type system or a schema already guarantees: a field exists, a value decodes to its own shape, a capability or config object has its declared values. |
| `trivial-logic` | covers code with no branch worth guarding: a getter, a constant, a pass-through, a default value, string formatting. |
| `framework-behavior` | checks the framework or platform, not this code: a render, a click handler, DOM presence, routing, IPC plumbing, store wiring. |
| `timing` | depends on real or fake wall-clock time: sleeps, timers, polling, retry-until-true, waits for frames or transitions, elapsed-time asserts. Not this category when the code under test reads a deterministic test clock (Effect `TestClock`) and the test checks a security or scheduling rule. |
| `mock-mirror` | asserts that a mock was called with the arguments the implementation passes. |
| `smoke` | only checks that something imports, mounts, does not throw, or is defined. |
| `perf-wallclock` | asserts a duration, throughput or memory number measured on the host. |

## Keep

| Category | Keep when the test |
|---|---|
| `orchestration` | checks backend orchestration or event-sourcing correctness: command and event ordering, server-side projections, state transitions across processes or services, idempotency, recovery after restart. Client UI state is `ui-logic`. |
| `protocol` | checks translation to or from an external protocol, provider API, wire format or CLI output, including backward-compatible decoding. |
| `security` | checks auth, permissions, credential or session expiry, scope narrowing, secret redaction, input validation at a trust boundary. |
| `persistence` | checks storage, migrations, schema upgrades, data written and read back. |
| `parsing` | checks parsing of external formats: user input, config files, dates, timezones, DST, paths across OSes, encodings. |
| `race-fix` | is a deterministic regression test for a concurrency or ordering bug. |
| `regression` | names or links an issue or incident, or pins the exact edge case a bug fix introduced. |
| `guard` | is documented as intentional: a tool upgrade guard, a patched dependency guard, a performance budget the project enforces on purpose. |
| `negative-property` | proves a security or data property must not happen: a secret never reaches a log, access fails after revoke, a cancelled job never runs. |

## Sensitive keywords

`guard.py` checks the file path and test path for these words (case-insensitive, word parts of camelCase and snake_case count).

Hard words name a security or data property. A delete that hits one is kept without review:

permission, scope, acl, rbac, credential, password, secret, redact, token, jwt, oauth, csrf, xss, injection, encrypt, decrypt, signature, nonce, privacy, pii, gdpr, migration, migrate, ledger, payment, invoice, balance, dst, daylight, timezone.

Soft words are often security terms but also everyday names (a chat session, a role in a list, a restore button). A delete that hits one goes to review:

auth, role, session, expiry, expire, cors, sanitize, escape, schema, tz, money, amount, fee, decimal, rounding, sign, verify, crypto, hash, backup, restore, delete, purge.

## Review

`review.py` reads this section. A stronger model re-checks each delete that the guard moved to review. You get the whole test file, the guard reasons and the classifier's reason, and read-only tools to open the production code and search the repo.

The suite is being cut hard on purpose, and losing a test of presentational behavior is an accepted cost. Keep the test only when it is the last check in the repo of one of these:
- a security or data property: access, secrets, persistence, money, time and timezone math,
- a negative property: something must not happen (a leak, a write after revoke, work after dispose or cancel),
- a contract with something outside this code: a wire or file format, a protocol, a CLI or doc that other code or people rely on,
- the edge case a bug fix changed (see below).

Delete everything else: UI and view logic, layout, labels, menus, filters and sorting for display, error wording, input variants, and behaviors a stronger test already covers. A delete of presentational or variant behavior needs no `covered_by`.

When the guard shows a fix commit, the test was added with that fix. Keep it when it reproduces the fixed bug: its input or state is the one the commit subject describes, or it asserts the exact edge the fix changed. A sibling test of the same function that does not reach that edge does not cover it.

Two kinds of delete must prove a surviving test covers the behavior: a test added by a fix commit, and the last test of a production symbol whose deletion also empties its whole file. For these, name the covering file in `covered_by` and copy into `evidence` one line from that covering test, exactly as written, where it sets up or asserts the same input or state. The line is checked against the file, and a delete whose evidence is missing, not found, or found only inside the test being deleted is turned into keep.

In security and permission code, each authorization decision is its own behavior: who acts, which action, in which state (granted, missing, revoked mid-operation, expired, each session state). An allowed path and a denied path are two behaviors. A test of one decision does not cover another.

Each verdict names the behavior.
