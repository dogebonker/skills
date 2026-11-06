# skills

Agent skills I use daily with Claude Code and Codex. Each one is a folder with a
`SKILL.md` and the scripts or templates it needs.

| Skill | What it does | Reach for it when |
| --- | --- | --- |
| [explain-decisions](skills/explain-decisions/SKILL.md) | Before the agent asks you to pick between technical options, it builds one local HTML page per decision: the choice in one sentence, a walk-through of a real example under each option, a blast-radius grid, a one-question quiz on the fact the choice depends on, its pick with the downside, and whose call it is. | You're asked "A or B?" about code you don't own yet. |
| [ui-references](skills/ui-references/SKILL.md) | Adapts Mobbin’s reference-driven redesign method to free public demos, official screenshots and a local library. Includes finance/crypto/AI references, design-kit checks, before/after evidence and a UI/UX benchmark against 2–3 products; no paid reference service or multi-provider council required. | You want UI polish, reference research, or a comparison of design directions. |
| [bug-review](skills/bug-review/SKILL.md) | Runs the scanners you already have (gitleaks, ruff, shellcheck, actionlint, golangci-lint, clippy, eslint/biome, semgrep) on changed files, then checks the diff against a checklist built from 673 real CodeRabbit findings. Reports only verified findings, with severity and effort. | Before opening a PR. |
| [approach-review](skills/approach-review/SKILL.md) | Checks architectural necessity and guarantees by tracing state writers, consumers, locks, permissions and recovery, then verifies the review against the original contract. | Reviewing new jobs/services, shared lifecycle changes, recurring reads, retries or state migrations. |
| [feature-pipeline](skills/feature-pipeline/SKILL.md) | Takes a large feature through interview and docs, two architect/critic rounds, tests written against the plan, and then implementation slices that each verify before the next one starts. | A new project or a multi-module feature. Not for small fixes. |
| [choose-architecture](skills/choose-architecture/SKILL.md) | Picks the system shape for a new project or a new service before any code, or the target shape and a step-by-step migration path for a running system. It numbers the functional and non-functional requirements, does the capacity arithmetic, sketches at least two candidates (a modular monolith by default), screens them for red flags, and backs each decision with a quoted rule from the book that owns that kind of decision, plus a "revisit when" trigger. Ships rules for LLM components built from vendor and OWASP sources, and house stack defaults. | "What architecture should we use?", monolith or microservices, a new service joining an existing system, splitting a monolith or replacing a store. |
| [test-snap](skills/test-snap/SKILL.md) | Deletes low-signal tests in bulk the way t3code PR #22557 cut 11k of 26k tests: a Haiku swarm judges each test, guards and a Sonnet reviewer protect the last test of security, data and contract behaviors, deletions apply by AST range with a parse and compile check, and before/after timing measures the win. TS/JS, Python, Rust, Go. `evals/` replays the PR against what the t3 team kept after its restores. | CI is slow or flaky from too many tests. |
| [brief](skills/brief/SKILL.md) | Cuts a long thread down to status, what needs your decision, and the next step. | The reply was a wall of text, or a long multi-agent run just finished. |
| [show-me](skills/show-me/SKILL.md) | Explains the current topic with a diagram, a sketch of the code's shape, or a small HTML page. | Text alone isn't landing. |
| [explain](skills/explain/SKILL.md) | Explains how project code works one layer at a time, starting from the problem it solves and going down to `file:line`, deeper or simpler on request. | You're onboarding to a subsystem, or "how does X work?" |
| [use-patterns](skills/use-patterns/SKILL.md) | Scans code with per-language searches for places where a GoF pattern, DRY, KISS or SOLID would help, and for patterns that cost more than they give. Confirms each against a catalog, prefers the smallest idiom, and plans the refactoring. Ships fixtures and an answer key in `evals/`. | Reviewing a codebase for duplication, over-engineering or design-principle problems. |
| gof-patterns: [go](skills/gof-patterns-go/SKILL.md), [javascript](skills/gof-patterns-javascript/SKILL.md), [kotlin](skills/gof-patterns-kotlin/SKILL.md), [python](skills/gof-patterns-python/SKILL.md), [rust](skills/gof-patterns-rust/SKILL.md), [swift](skills/gof-patterns-swift/SKILL.md), [typescript](skills/gof-patterns-typescript/SKILL.md) | The 22 GoF design patterns per language, each with a runnable example and when not to use it. | Implementing or reviewing a design pattern. |
| solid-patterns: [go](skills/solid-patterns-go/SKILL.md), [javascript](skills/solid-patterns-javascript/SKILL.md), [kotlin](skills/solid-patterns-kotlin/SKILL.md), [python](skills/solid-patterns-python/SKILL.md), [rust](skills/solid-patterns-rust/SKILL.md), [swift](skills/solid-patterns-swift/SKILL.md), [typescript](skills/solid-patterns-typescript/SKILL.md) | SRP, OCP, LSP, ISP and DIP as they read in each language, each with a violation and its fix side by side. | Designing or refactoring modules and interfaces. |
| [dry-patterns](skills/dry-patterns/SKILL.md) | DRY and its limits: single source of truth, rule of three, wrong abstraction, magic values. | Deciding whether to deduplicate code. |
| [kiss-patterns](skills/kiss-patterns/SKILL.md) | KISS: YAGNI, speculative generality, guard clauses, boring technology, pattern overuse. | Code feels heavier than the problem. |

## Install

Copy a skill folder into your agent's skills directory, for example
`~/.claude/skills/` or `~/.agents/skills/`. These are snapshots and do not
update an installed copy.

- `approach-review` is validated for Codex with a native `verifier` agent and same-context continuation. Claude instructions and a companion agent are bundled, but Claude qualification is pending.
- `bug-review` uses whichever of the listed scanners are installed and skips the rest.
- `feature-pipeline` calls other skills named in its `SKILL.md` that are not bundled here.
- `choose-architecture` reads book rule files from [ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books) at `~/.agents/skills/<book>/<book>.mini.md` (seven books), and the `codebase-design` vocabulary. `references/stack.md` holds my own stack defaults: edit it to yours.
- `test-snap` needs `uvx` (it fetches ast-grep) and the `claude` CLI, and spends model credits: about $4 per 1,000 tests on t3code.
- `use-patterns` links to the pattern skills here and to a separately installed `refactoring-guru` skill.
- Some commands assume Claude Code and may need small changes for other agents.
