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

## Install

Copy a skill folder into your agent's skills directory, for example
`~/.claude/skills/` or `~/.agents/skills/`. These are snapshots and do not
update an installed copy.

- `bug-review` uses whichever of the listed scanners are installed and skips the rest.
- `feature-pipeline` calls other skills named in its `SKILL.md` that are not bundled here.
- Some commands assume Claude Code and may need small changes for other agents.
