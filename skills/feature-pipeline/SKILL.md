---
name: feature-pipeline
description: Automated multi-agent pipeline for a BIG feature or a NEW project — grill-with-docs (interview + CONTEXT.md/ADRs) → architect+critic in 2 rounds (delivery plan + balanced architecture) → tdd (tests covering the plan) → sequential implementation subagents that verify each slice. Use when starting a substantial new feature or a new project that warrants real docs, architecture, and test coverage. Do NOT use for small edits, bugfixes, or one-file changes.
triggers: ["new feature", "new project", "big feature", "start a project", "build a feature", "feature pipeline", "deliver this feature"]
level: 4
---

# Feature Pipeline

An automated framework that takes a big feature or a new project from a vague idea to
implemented, tested code by chaining Matt Pocock's docs/test skills with OMC's planning
and execution agents. This is the replacement for the old `superpowers` "build" pipeline.

The spine: **grill → architect+critic ×2 → tdd → implement (sequential, verified)**.

## When this fires

- **Auto-suggest on trigger.** When the user starts a *big* feature or a *new* project,
  announce that you're starting the pipeline and run Phase 1 (grill). Before any phase that
  spawns subagents (Phases 2 and 4), get a quick go-ahead — don't burn agent tokens silently.
- **Scope gate (anti-overpush on process).** This pipeline is itself a heavy abstraction.
  Apply the same balance you apply to code: don't run a 5-phase, multi-agent pipeline for a
  small thing. If the work is a bugfix, a one-file change, a rename, or anything a single
  `tdd` pass or direct edit covers, say so and **skip to the right lighter skill** (`tdd`,
  `diagnose`, or a direct edit). Only run the full pipeline when the work genuinely spans
  multiple modules / needs design decisions / is a new project.

## The balance doctrine (carry this into every phase)

The whole point of the architecture phase is **proper balance**, not maximal structure.
Inject this verbatim into the architect and critic prompts, and hold yourself to it:

- **Depth over count.** Prefer a few deep modules (large behaviour behind a small interface)
  to many shallow ones. Measure depth as *leverage at the interface* — see
  [LANGUAGE.md](../improve-codebase-architecture/LANGUAGE.md) for the exact vocabulary
  (Module, Interface, Depth, Seam, Adapter, the deletion test).
- **The deletion test.** For every proposed module/file/abstraction: if you deleted it, would
  complexity vanish (it was a pass-through — cut it) or reappear across N callers (it earns
  its keep — keep it)?
- **One adapter is a hypothetical seam; two is a real one.** Don't introduce an interface/seam
  until something actually varies across it. No speculative generality.
- **SOLID where it earns its keep, not everywhere.** Apply SRP/OCP/etc. and remove known code
  smells (god object, feature envy, shotgun surgery, primitive obsession, long parameter
  lists) *only* where they cause real friction. Naming a principle is not a reason to add a file.
- **Simplify by default.** The smallest design that satisfies the requirements wins. Ten files
  for a small thing is a failure, the same as zero structure for a large thing. The critic
  rejects **over-design as firmly as under-design.**

## Phase 1 — Discovery & docs  (interactive, no subagents)

Run the **`grill-with-docs`** skill in this conversation. Interview the user one question at a
time, stress-test terminology against the codebase, and capture decisions inline:

- `CONTEXT.md` (and `CONTEXT-MAP.md` if multi-context) — the domain glossary, created lazily.
- `docs/adr/NNNN-*.md` — only for decisions that are hard to reverse, surprising, and a real
  trade-off (grill-with-docs' own bar).

**Exit criterion:** a crisp, written feature brief — what we're building, the domain terms,
the constraints, and the explicitly-resolved ambiguities. If the repo has no `CONTEXT.md`/
`docs/adr/` yet and this is a new project, this phase seeds them. Consider running
`setup-matt-pocock-skills` first if the repo's doc layout / issue tracker isn't configured.

## Phase 2 — Architecture & delivery plan  (2 rounds; subagents — confirm first)

Goal: a **balanced architecture** plus a **phased delivery plan**. Break the work into ordered
**phases**, where each phase is one independently-implementable vertical slice that (a) has its
dependencies and test surface named, (b) leaves the repo green and working on its own, and (c)
ends with a **Commit** step. Phases are the unit the user reviews and commits — size them so a
single phase's diff is reviewable in one sitting (not too big to read, not so tiny they're noise).

Run exactly two rounds. Pass the balance doctrine (above) into every prompt.

- **Round 1 — draft.** Dispatch the **`architect`** agent (Opus, read-only) with the Phase 1
  brief. Ask it to produce: (a) module decomposition with an explicit deep/shallow analysis per
  module using the LANGUAGE.md vocabulary, (b) where SOLID/smell-removal is and isn't warranted
  *and why*, (c) a delivery plan as ordered vertical slices with dependencies and the public
  behaviours each slice must expose. It cites `file:line` for anything touching existing code.
- **Round 1 review.** Dispatch the **`critic`** agent (Opus) on the architect's draft. Require it
  to check **both directions**: under-design (missing depth, ignored smells, untestable seams)
  **and** over-design (unnecessary files, premature abstraction, one-adapter seams, indirection
  for small things — apply the deletion test). Output: structured findings + an approve/revise verdict.
- **Round 2 — revise.** Dispatch **`architect`** again with the critic's findings. It resolves
  each finding and produces the final architecture + **phased delivery plan**, emitted in the
  exact shape of [PLAN-TEMPLATE.md](./PLAN-TEMPLATE.md) — every phase lists its goal, dependencies,
  files/modules touched, the tests that prove it, a verify step, and a final **Commit** message.
  Write it to `docs/adr/` (for the decisions) and a delivery-plan doc (e.g. `docs/plans/<feature>.md`
  or `.omc/plans/<feature>.md` — follow whatever the repo already uses).
- **Round 2 review.** Dispatch **`critic`** for final sign-off: approve, or list residual risks.

**↪ GATE 1 (human).** Present the locked architecture + sliced plan to the user in a compact
summary (modules, why this shape, the slices, residual risks). Get explicit approval before
proceeding. Incorporate edits.

## Phase 3 — Test-first  (tdd)

Run the **`tdd`** skill. For each slice in the approved plan, write tests that exercise the
**public interface / behaviour** named by the architect — integration-style, not implementation
detail (a test reads like "user can checkout with valid cart"). Tests should be red now and
become the executable spec for implementation. Do **not** write implementation yet.

**↪ GATE 2 (human).** Present the test list (one line per behaviour, mapped to slices) so the
user can confirm the tests capture the intended spec before any code is written. Adjust on feedback.

## Phase 4 — Implementation  (phased: implement → verify → commit → review, one phase at a time; subagents — confirm first)

Work **one phase at a time** in dependency order. Each phase ends in a commit and a review
checkpoint, so you can inspect the diff and ask for edits before the next phase starts. This is
the superpowers-style cadence: small, green, committed phases the user can verify and redirect.

**Before the first phase — branch.** Never commit the pipeline's work directly onto `main`/
`master`. If the repo is on its default branch, create a feature branch first (or get explicit
consent to commit on the current branch). This repo's default is `master`.

For each phase:

1. **Implement.** Dispatch an **`executor`** agent (Sonnet; `model=opus` for a complex phase)
   scoped to that single phase. Hand it the phase's tests, the architect's module spec for the
   phase, and the balance doctrine. Instruct: smallest viable diff, no new abstractions for
   single-use logic, make the phase's tests green.
2. **Verify.** The phase's tests pass (fresh output, not assumed) and `lsp_diagnostics` is clean.
   If red, iterate on this phase (or route to `diagnose`) — never build the next phase on a broken one.
3. **Commit.** Commit *just this phase*, following the repo's existing commit convention (recent
   history is Conventional Commits, `feat: …`) plus the required `Co-Authored-By` trailer. One
   phase = one focused commit that leaves the tree green.
4. **↪ Review checkpoint (human).** Show a compact diff summary for the phase — files touched,
   what changed, which tests are now green — and **pause**. The user verifies and either approves
   (→ next phase) or requests edits. Apply edits as follow-up commits (or amend the phase commit
   if they prefer), re-verify, then continue. Do not start the next phase until they're satisfied.
5. Repeat for the next phase.

The phased commit-and-checkpoint cadence is the whole point: every phase is a reviewable,
revertable unit, errors can't compound across phases, and the user can redirect between any two
phases. (If the user says "don't pause between phases," run straight through but still commit each
phase, so the history stays bisectable and reviewable after the fact.)

## Phase 5 — Final verification & handoff

- Run the full test suite + build; show fresh output.
- Dispatch **`verifier`** (or `critic` for a security/quality-sensitive change) for an
  independent completion check against the Phase 1 brief and the approved plan — separate lane
  from whoever implemented.
- Summarise: what was built, the docs/ADRs produced, phases delivered (one commit each), tests
  added, and any residual risks the critic flagged.
- **Finish the branch.** Offer next steps — open a PR or merge — but **don't push or open a PR
  unless the user asks** (mirrors `finishing-a-development-branch`). The phased commits are
  already on the feature branch for them to review.

## Notes

- **Separation of lanes:** never let the agent that implemented a slice also be the one that
  approves it. Authoring and review stay in different passes (executor implements; verifier/critic approves).
- **Docs location:** follow the repo's existing convention (`CONTEXT.md` + `docs/adr/`, plus a
  plan doc). Don't invent a parallel structure if one exists.
- **Determinism option:** the Phase 2 architect↔critic rounds and the Phase 4 per-slice loop are
  good candidates to run as a `Workflow` script if the user explicitly opts into orchestration;
  otherwise drive them with the `Agent` tool as described above.
