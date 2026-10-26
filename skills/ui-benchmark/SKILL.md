---
name: ui-benchmark
description: Free, local Mobbin-style screen library plus a benchmark loop. It collects real screens of similar apps (App Store screenshots, headless Chrome captures including logged-in apps, user screenshots), scores every app and the target on the same heuristics, and shows a side-by-side ranking board with good and bad pins. Once the user agrees with the ranking, it raises the target's UI with impeccable inside DESIGN.md and PRODUCT.md and proves the result with before/after captures. Use when a feature has no UI design yet, when the user wants to see how similar apps handle a screen or flow, asks for UI references or inspiration, mentions Mobbin, or wants their UI compared or ranked against competitors.
---

# UI benchmark

Learn from apps that already solved this screen, then raise ours. Borrow patterns, not pixels: never copy another product's logo, illustrations, copy or exact layout.

`<skill>` is this folder, `~/.claude/skills/ui-benchmark`. The library lives in `~/.design-library` (override with `$DESIGN_LIBRARY`) and is shared across projects. Browse it with `node <skill>/library.mjs gallery`. `<workspace>` is the folder that holds the project's repo, for example `~/Work/acme` for `~/Work/acme/app`.

## Rules

- PRODUCT.md and DESIGN.md are the authority. An idea that needs a colour, font, token or rule they don't allow is the user's decision (use `explain-decisions`). Never edit either file without an explicit yes.
- Score every app, the target included, with one rubric: the Heuristics Scoring Guide in `~/.claude/skills/impeccable/reference/critique.md` (Nielsen's 10, 0 to 4, `null` for n/a). Same rubric, same flow, same screen sizes, or the ranking means nothing.
- App Store screenshots are staged marketing. Prefer real captures, and say on the board which screens are marketing.
- Ask before using the user's accounts for logged-in captures. Use demo or test workspaces, never other people's private data. The login profile is kept in `~/.cache/ui-benchmark/chrome-profile`, outside the library, with owner-only permissions.
- Never point `$DESIGN_LIBRARY` at a synced or committed folder.
- Screens, library and boards stay local. They're reference material, not assets to ship.
- Use `impeccable` for the build because it keeps DESIGN.md. Don't use `hallmark` to design here: its dealt themes override an existing system. Only its linter is used, in step 9.

## Steps

1. **Context.** Run `~/.claude/skills/impeccable/scripts/impeccable context --target <feature path>` from the project, and read PRODUCT.md and DESIGN.md. Write one sentence naming the feature and the one flow to compare, for example "reading and resolving comments on a document".
2. **Pick 3 to 6 reference apps.** Start from the user's list. Propose up to 3 more from the same field with a one-line reason each, and confirm the list with AskUserQuestion before collecting.
3. **Collect that flow's screens, cheapest first** (`node <skill>/library.mjs ...`):
   - `search <app> <flow>`: reuse what the library already has.
   - `capture <url> --app A --flow F [--note "..."]`: public pages at 1440×900. `--phone` gives 390×844 at 2× (780px-wide files), and `--full` the whole page, up to 8000px. A warning about ending on another URL usually means a sign-in or error page, so delete that capture.
   - Behind a login: `login <url>` once. The user signs in, then quits that Chrome completely, because capture refuses while it's open. Then run `capture ... --logged-in`.
   - Mobile apps: `appstore "<name>"`, or `--mac` for Mac apps.
   - Help-centre articles often show the exact feature: `add <image URL> --app A --flow F --platform web --source <article url>`.
   - Anything else: ask the user for screenshots, then `add <files> --app A --flow F --platform P`.
   - Capture the target too, from its dev server URL, with the same sizes and the target's name as `--app`. Use a demo account, because the target's captures stay in the shared library.
4. **Score and annotate.** For each app, record:
   - its 10 scores
   - visual notes on colour, type, layout and states
   - 2 to 4 pins per screen, each with `x` and `y` as percentages, `good` or `bad`, and a note of 15 words or fewer
   - a one-line verdict

   Look at every screen before scoring it. Never score from memory of the product.
5. **Board.** Copy [template.html](template.html) to `<workspace>/design-benchmarks/<feature>/index.html`, outside any git repo, and replace only the JSON in `<script id="data">`. Image `src` takes absolute paths from the library; remote URLs are rejected so the board stays local. Run `node <skill>/check.mjs <board>` until it prints `ok`, then open it (`open` on macOS, `xdg-open` on Linux).
6. **Agree on the ranking.** AskUserQuestion: does this ranking match your taste? Options: Agree, Reorder (tell me how), or Add or drop an app. If they disagree, ask what they value that the scores missed, re-score, and record their words in `userVerdict`.
7. **What to borrow.** From the top apps, list concrete ideas, each tagged:
   - `fits`: DESIGN.md already allows it.
   - `change`: it needs a DESIGN.md or PRODUCT.md change, so the user decides and you name the rule in `designRef`.
   - `conflicts`: dropped, with the reason.

   Confirm the list.
8. **Build with impeccable.** For a feature with no UI, run `shape`, then build. For an existing UI, use the matching refine commands (`layout`, `typeset`, `colorize`, `clarify`, `polish`). Read `reference/craft-floor.md` before editing. Use only `fits` ideas and approved `change` ideas.
9. **Prove it.**
   - Capture the target again with the same URL and sizes.
   - Fill `compare`: before, after, the best reference, pins on the after screen, and `scoresAfter`. Score it the same way as step 4.
   - Run `check.mjs` and `open` the board.
   - For web targets, also run `node ~/.claude/skills/hallmark/scripts/sloplint.mjs <files> --scope app --render` if it's installed. Fix failures that don't contradict DESIGN.md.
   - Stop after 2 build-and-compare rounds and hand back what's left.
10. Run `node <skill>/library.mjs gallery` to refresh the library's browsable index.

## Board data

- **Top level:** `title`, `feature`, `flow`, `constraints[]` (the DESIGN.md and PRODUCT.md rules in play), `userVerdict`, `apps[]`, `borrow[]`, and optionally `compare`.
- **Each app:**
  - `name`, `target: true` on the user's app only, `why`, `verdict`
  - `screens[]` of `{src, caption, pins[] of {x, y, kind, note}}`
  - `scores[10]`
  - `visual` with `color`, `type`, `layout` and `states`
- **Each borrow idea:** `idea`, `from`, `lands` (where it goes in the target), `fit` (`fits`, `change` or `conflicts`), and `designRef`.
- **compare:** `before`, `after`, `reference`, `referenceApp`, `pins[]`, `scoresAfter[10]`.

The template's JSON is a full worked example with mock screens.
