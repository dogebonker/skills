---
name: explain
description: Explain how something in a project works one layer per round, starting from the problem it solves and going deeper or simpler when the user asks. Use for "how does X work", "explain X", "I don't get X", onboarding to a subsystem, or when the user replies "simpler" or "deeper on Y" to an explanation.
---

# Explain

Build the user's mental model of one thing, one **layer** per round. The user steers.
Every round fits in about 15 lines and ends with where to go next.

## Layers

| Layer | Answers | Shape |
| --- | --- | --- |
| L0 Problem | What breaks, and for whom, if this did not exist? | One or two sentences in the user's words. No project names. |
| L1 From nothing | If nothing existed, what is the least you would build to solve L0? | Three to five parts, one line each, still no project names. |
| L2 This project | Which real code plays each L1 part, and how does a request flow through it? | One call tree or sequence diagram, each step with `file:line`. A part with no code is a gap, so say so. When there are several entry points, list them and trace the one asked about. |
| L3 One part | What happens inside the part the user picked? | Data shapes, decision points, failure paths, gotchas, with `file:line`. |

Round one gives L0 and L1 together. Later rounds move one layer per reply:

- **deeper on Y**: go one layer down, only for Y. From L1 that means Y's slice of L2, not the whole flow.
- **deeper**: go one layer down for everything in the current round.
- **simpler**: say the current layer again in fewer, plainer words. The previous round's `file:line` refs still stand, so they can be left out. If the layer is already at its plainest, go up one.
- **page**: render the explanation so far as one HTML file. Use the `show-me` skill when it is installed. Otherwise write the file to the scratch directory and open it.

End every round with one line of next moves that name the parts from that round, for example
`deeper: indexing · search · citations | simpler | page`.

## Evidence

Read the code before you claim something about it. Docs, design records, tickets, and what people
said are claims to check against the code, never the answer itself. If the code and a doc
disagree, report both and say which one runs. Name the commit (`git rev-parse --short HEAD`) in the first L2 round, and again only if it changes.
Mark anything you could not trace as `unverified:` and say why.

The user's corrections in earlier rounds outrank existing framing. If they say "forget that doc"
or "treat it as if we had nothing", drop the doc's vocabulary and rebuild from L0.

## Words

- Each round adds at most two new terms, each defined in plain words where it first appears.
  Reuse terms the user has already used and stop defining them.
- Use the code's real names from L2 down, and plain names above that.
- Describe the mechanism itself. Use a diagram only where prose would need a full paragraph
  to show the flow.

## Exploring

For a module or a narrow question, read the code yourself.

When the question covers a whole subsystem across services or many packages, not one path through it, run 2 to 4 read-only explore subagents
in one message before the first round. Give each one a separate angle, such as the entry point,
storage, external services, or background jobs. Ask each one for:

- the components it found, each with path and one line
- the flow step by step, with `file:line`
- the boundaries, meaning inputs and outputs to other parts
- anything non-obvious
- open questions

Keep the merged findings in a scratch notes file and answer later rounds from it. Read
more code only when a round goes below what the notes cover.

The work is done when the user stops asking, or when the L2 flow has every step pinned to
`file:line` and every gap is named.
