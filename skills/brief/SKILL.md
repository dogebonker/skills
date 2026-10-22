---
name: brief
description: Compress the current state of work into a short, decision-focused brief — status, what needs the user's decision, and the next step. Use when the user asks for a brief, a summary, TL;DR, "short version", "what do you need from me", or says the reply was too long. Also use proactively at the end of long investigations or multi-agent runs, when a wall of detail would bury the actual ask.
---

# Brief

Restate the current state of work in the fewest words that still let the reader act.

The reader is busy and is not reading the long version. Assume they have read
nothing since their last message. Anything they must decide has to be visible in
one screen, or it does not reach them.

## Output contract

Target 15 lines. Hard ceiling 25. Sections, in this order, omitting any that are empty:

**Status** — 1–2 lines. What is true now, not what happened.

**Needs you** — numbered. Each item is one answerable question, ≤2 lines, with the
options where options exist. Put the blocking one first. If something has been
asked before and not answered, keep it here rather than dropping it.

**Blocked / at risk** — only if real. Name the thing and what unblocks it.

**Next** — 1 line. What proceeds without them.

If nothing needs them: say so in one line and stop.

## Rules

- No preamble, no restating the request, no "here's what I did".
- Report state, not narrative. `be/MOB failing at 37%` — not the story of finding it.
- Numbers only when they change a decision. One number beats three.
- Never soften or omit bad news to save space. Brevity is not optimism: a failed
  test, a broken deploy, a wrong earlier claim stays in, compressed.
- Never invent a resolution for something still unresolved or still running.
- No hedging ("it seems", "possibly") unless the uncertainty itself is the point —
  then state it as a one-line confidence, e.g. `unverified: only 3 samples`.
- Links and paths over descriptions: `docs/foo.md, branch bar` beats a paragraph
  about where the doc lives.
- Keep verbosity out of the brief, not out of the work. The long version stays
  available — this replaces how it is *reported*, never how carefully it was done.

## Shape

```
**Status:** <one line of current truth>

**Needs you:**
1. <question> — <options, or the cost of each choice>
2. <question>

**Blocked:** <thing> — needs <what>

**Next:** <what continues without them>
```
