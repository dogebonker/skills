# Evals

| Round | Planted code | Answer key |
|---|---|---|
| 1 | `fixtures/<lang>/` | `expected.md` |
| 2 | `round2/<lang>/` | `expected-round2.md` |

A blind run:
1. Copy the round's code directory to a place outside the skill (`cp -R evals/round2 <scratch>/round2`) and point the skill at that copy only, one scope per language directory, with `REPO_ROOT` set to that language directory. The round-2 key names the planted dead functions, so a `REPO_ROOT` that contains a key makes signal 24 count them as used.
2. Write the report in the SKILL.md format, one `## Findings: <lang>` section per language.
3. Score it: `python3 -I evals/score.py <report.md> --key evals/expected-round2.md` (the default key is `expected.md`; `--json` prints the same result as JSON). The headline numbers assume every matched fix is in the expected direction, so tick each pair under "Check fix direction" by hand.

The scorer matches on file basenames and line numbers, so a copy scores the same as the original.
