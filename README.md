# Personal skills

A hand-picked collection of custom AI coding skills.

| Skill | Purpose |
| --- | --- |
| [brief](skills/brief/SKILL.md) | Short, decision-focused status summaries. |
| [bug-review](skills/bug-review/SKILL.md) | Evidence-based defect reviews with installed static scanners. |
| [feature-pipeline](skills/feature-pipeline/SKILL.md) | A staged workflow for substantial features and new projects. |
| [show-me](skills/show-me/SKILL.md) | Concise visual explanations and diagrams. |

Each folder contains a `SKILL.md` and any supporting files. These are snapshots
of the selected local skills; installed copies are unchanged and do not sync
automatically with this repository.

## Use

Copy a selected skill folder into your agent's skills directory, for example
`~/.agents/skills/`. Review an existing installation before replacing it.

`bug-review` uses whichever supported scanners are already installed.
`feature-pipeline` expects the orchestration and related skills named in its
instructions; those dependencies are not bundled here. Agent-specific commands
may need adapting for a different environment.
