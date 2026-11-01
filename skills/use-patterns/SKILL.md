---
name: use-patterns
description: "Find where GoF patterns, DRY, KISS or SOLID would improve code, or where a pattern costs more than it gives, and plan the behavior-preserving refactoring. Use when reviewing code for duplication, over-engineering or design-principle violations, or when asked where a pattern applies."
---

# Use Patterns

Find where a GoF pattern would pay, where code repeats knowledge (DRY), where it is more complex than the problem (KISS, including patterns that do not pay), and where it breaks a SOLID principle. Every verdict rests on evidence read from the code.

Reference, loaded when a step says so:
- [`reference/signals.md`](reference/signals.md): ripgrep searches per language, each tagged with the catalog entry it feeds, and the triage command. Its helpers live in `scripts/`.
- [`reference/catalog.md`](reference/catalog.md): one entry per finding, grouped by family, with confirm questions, counter-signals, neighbours, the idiom, steps and a before-shape.
- Target files, under `~/.claude/skills/`:
  - GoF: `gof-patterns-<lang>/patterns/<id>.md` with `examples/<id>.<ext>`.
  - DRY: `dry-patterns/patterns/<id>.md` with its example.
  - KISS: `kiss-patterns/patterns/<id>.md` with its example.
  - SOLID: `solid-patterns-<lang>/patterns/<id>.md` with `examples/<id>.<ext>`.
- `~/.claude/skills/refactoring-guru/`: small-step refactoring mechanics (Extract Method, Move Method, Remove Middle Man and the rest).

| Language | `<lang>` | `<ext>` | Files |
|---|---|---|---|
| JavaScript | `javascript` | `js` | `.js .mjs .cjs .jsx` |
| TypeScript | `typescript` | `ts` | `.ts .tsx .mts .cts` |
| Go | `go` | `go` | `.go` |
| Rust | `rust` | `rs` | `.rs` |
| Kotlin | `kotlin` | `kt` | `.kt .kts` |
| Swift | `swift` | `swift` | `.swift` |
| Python | `python` | `py` | `.py` |

## Steps

1. **Scope**: list the files in scope and the language of each, from the table above. Leave out generated and vendored code; keep tests, since a test double can justify an interface. For a language outside the table, adapt the closest section of `signals.md` and say so in the report. Check history with `git rev-parse --is-shallow-repository` (true, or an error outside git, means no usable history). Done when every file is listed with its language and line count, every excluded path is named, and the history state is known.

2. **Scan and triage**: from each scope directory, run the language's `sh` block in one call and save the output: `awk '/^## Go$/{f=1} f&&/^```sh$/{b=1;next} b&&/^```$/{exit} b' <skill dir>/reference/signals.md | SKILL_DIR=<skill dir> REPO_ROOT=<repo root> RG_EXCLUDE='<glob>' bash -v > <scan file> 2>&1`, with the language's heading in place of `Go`. Drop `RG_EXCLUDE` when nothing under the scope directory is excluded; `signals.md` (Running a block) explains the three variables. `bash -v` prints each `# ID` above its hits. Then run the triage command from `signals.md` (Triage) on the scan file, with the same `RG_EXCLUDE`. It clusters the hits by enclosing function and ranks the clusters by hit count, then function length.
   - Read every list under `# lists`.
   - Read the clusters in rank order: each enclosing function in full, plus every other place that branches on the same value, repeats the same literal or rule, or calls the same API. Each hit in a read cluster becomes a candidate (file:line and signal ID) or is discarded with a one-line reason.
   - Read every cluster with 3 or more hits. When more than 40 clusters have 3 or more hits, read the first 40. Clusters marked `[boundary]` (type checks in parsing code, ranked last) are left unread. The hits in unread clusters go on the report's not-triaged line.

   Done when clusters 1 to k are all read with every hit accounted for, and the not-triaged count (total hits minus the cumulative hits at rank k) and its cluster count are written down.

3. **Confirm**: give each candidate a family: GoF opportunity, DRY violation, KISS violation, or SOLID violation. KISS includes pattern overuse: a pattern, interface, factory, singleton or wrapper that costs more than it gives. Open the catalog entry the signal feeds and answer its Confirm questions with evidence from the code:
   - how many variants or copies;
   - how many places branch on or repeat the same thing;
   - the change history (`git log -L :<function>:<file>`, or churn with `git log --oneline -- <file> | wc -l`). With a shallow clone or no git, answer each history question "n/a (no history)" and judge the finding on the remaining answers (see Confidence).

   Apply the rule of three and every counter-signal. Use the entry's Neighbours line to pick between look-alikes and to find which entry owns a smell that two families share. Merge candidates with one root cause into one finding. Done when:
   - each candidate is CONFIRMED (with its evidence, family and id), WEAK (as defined at the top of `reference/catalog.md`) or REJECTED (with the counter-signal that rejected it);
   - every pattern, interface, factory, singleton and wrapper in scope (signals 8, 9, 10 and 14) is either a KISS finding or cleared with a reason.

4. **Simplest fix first**: for each CONFIRMED finding, check the entry's Idiom first line for a language feature or plain refactoring that removes the smell, before any pattern structure. Open the target file when the Idiom line leaves the fix open, and for every SOLID finding. Language features: a function or map of functions, an enum or union with exhaustive match, a generator, a module, a guard clause, a named constant, a parameter. Plain refactorings, from `refactoring-guru`: Extract Method, Introduce Parameter Object, Replace Conditional with Polymorphism. Run every GoF or SOLID recommendation past the KISS entries: if one describes the structure you are about to add, the smaller fix wins. Done when every confirmed finding names its recommended fix and its target file, and says why the bigger option is or is not needed.

5. **Report**: the report is the deliverable, in the format below. Write it to a file when the environment allows; otherwise return it as text in the same format. Done when the scope header is complete, every CONFIRMED and WEAK candidate is a row with all fields, every REJECTED candidate is a line under Considered and rejected, and every signal with no hits is listed in one line.

6. **Refactor only on request**: when the user asks to apply a finding, follow its catalog steps as small behavior-preserving moves, using `refactoring-guru` mechanics. Run the tests before and after each move; where no test covers the code, first write one that pins today's behaviour. A review-only request ends at step 5 with the code unchanged.

## Rules

- A smell is a prompt to investigate, not a verdict (Fowler). The verdict comes from step 3.
- Under-engineering and over-engineering both cost (Kerievsky): a missing pattern shows as the same switch in many places, an extra one as indirection that nothing uses. Report both directions.
- One finding per root cause. If one `switch` on a type code appears in five files, that is one finding with five locations, and that spread (Shotgun Surgery) is its evidence. When two families describe the same smell, report it once under the family of the catalog entry that owns it and name the other as a secondary id.
- A pattern needs 2 or more variants today. Two similar code blocks wait for a third before extraction (rule of three). A business fact or rule (a rate, a list, a validation) gets one home from its second copy.
- Cite file:line for every claim.
- Judge an exported symbol by its callers. When the scope has none, search the whole repository (app, tests, scripts, entry points and config; signal 24 with `REPO_ROOT` at the root does this). With no hits there either, and no dynamic reference found, confidence may be high, and the evidence says the whole repository was searched. When only the scope was searched, set confidence to medium and make the first fix step that search.

When principles pull in different directions:
- **DRY against KISS**: prefer duplication over a premature shared abstraction. Extract on the third copy, and only what all copies share. Values that are equal by coincidence and change for different reasons stay apart. A shared function that grew a flag per caller is a DRY wrong-abstraction finding: inline it.
- **SOLID against KISS**: an interface, trait, protocol or extension point with one implementation and no test double is a KISS violation, not an OCP or DIP win. The first DIP fix is a parameter of the concrete type or a function; add an interface owned by the policy only when a second implementation or a test double needs it.
- **SOLID against SOLID**: for a closed set you own, an exhaustive match satisfies OCP better than a registry, because the compiler lists every site to change. Split for SRP only along reasons to change that exist today; a big class whose methods all serve one owner and one set of data is cohesive.
- **GoF against KISS**: a pattern recommendation must pass the KISS check in step 4. Anything that adds classes or interfaces has to remove more than it adds.

## Report format

```
## Findings: <scope>

Scope: <N> files, <L> lines (<language>: files, lines; one entry per language).
Excluded: <paths and globs left out, or "none">.
History: <"git history available", or "shallow clone" / "no git": history questions answered n/a (no history)>.
Not triaged: <hits> hits in <clusters> clusters below rank <k> (or "none").

| # | Family | Id | Where | Smell / signal | Evidence | Recommended fix | Confidence | Payoff vs cost |
|---|---|---|---|---|---|---|---|---|
| P1 | GoF | strategy (also SOLID ocp) | path:line (+ other locations) | Switch on type code | 4 variants, same switch in 3 files | map of functions (idiom) | high | removes 3 switches; one new type |
| P2 | DRY | single-source-of-truth | path:line, path:line | Country list written twice | 2 copies, one already differs | one constant, options derived | medium | one place to change |
| A1 | KISS | pattern-overuse | path:line | Interface with one implementation | 1 implementation, no test double | use the class directly | high | deletes 2 types |

Per finding, below the table:
- **P1 steps**: 3 to 6 behavior-preserving steps.
- **P1 target**: ~/.claude/skills/<skill>/patterns/<id>.md and its example.

## Considered and rejected
- path:line: <family> <signal> - <counter-signal that rejected it>
```

P codes are findings whose fix adds or reshapes structure, SOLID findings included, and A codes are findings whose fix removes structure (pattern overuse, needless indirection, speculative generality, premature optimization, a wrong abstraction, dead code), while a WEAK finding keeps its P or A code with confidence low. Codes stay stable so the user can answer "apply P1, skip A2".

A finding that came from the wider read in step 2 rather than from a scan hit says "from wider read" in its Evidence.

Confidence:
- `high`: CONFIRMED, and every Confirm answer rests on a count, a compiler or linter warning, tool output, or git history. Answers marked "n/a (no history)" are left out of this test; without history, high also needs at least 2 other Confirm answers that rest on counts, compiler output or tool output, and a finding with fewer is medium.
- `medium`: CONFIRMED, and at least one Confirm answer is a judgement about intent or future change.
- `low`: WEAK. Its steps say what evidence would confirm it.

Null Object has no gof-patterns file, so its target line names the catalog entry.
