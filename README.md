# skills

Agent skills I use daily with Claude Code and Codex. Each one is a folder with a
`SKILL.md` and the scripts or templates it needs.

| Skill | What it does | Reach for it when |
| --- | --- | --- |
| [explain-decisions](skills/explain-decisions/SKILL.md) | Before the agent asks you to pick between technical options, it builds one local HTML page per decision: the choice in one sentence, a walk-through of a real example under each option, a blast-radius grid, a one-question quiz on the fact the choice depends on, its pick with the downside, and whose call it is. | You're asked "A or B?" about code you don't own yet. |
| [ui-benchmark](skills/ui-benchmark/SKILL.md) | Collects real screens from similar apps (App Store, headless Chrome, your screenshots), scores them and your app on the same heuristics, and shows a side-by-side ranking board. Once you agree with the ranking, it upgrades your UI within `DESIGN.md` and `PRODUCT.md` and shows before/after captures. | A feature has no design yet, or you want to see how others solve a screen. |
| [bug-review](skills/bug-review/SKILL.md) | Runs the scanners you already have (gitleaks, ruff, shellcheck, actionlint, golangci-lint, clippy, eslint/biome, semgrep) on changed files, then checks the diff against a checklist built from 673 real CodeRabbit findings. Reports only verified findings, with severity and effort. | Before opening a PR. |
| [feature-pipeline](skills/feature-pipeline/SKILL.md) | Takes a large feature through interview and docs, two architect/critic rounds, tests written against the plan, and then implementation slices that each verify before the next one starts. | A new project or a multi-module feature. Not for small fixes. |
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

- `bug-review` uses whichever of the listed scanners are installed and skips the rest.
- `feature-pipeline` calls other skills named in its `SKILL.md` that are not bundled here.
- `use-patterns` links to the pattern skills here and to a separately installed `refactoring-guru` skill.
- Some commands assume Claude Code and may need small changes for other agents.
