---
name: ui-references
description: Hill-climb a screen or component of our product toward another product's UI and UX while keeping our own design kit and brand. Collects the reference screens into a local Mobbin-style library, turns them into a brand-neutral spec the user approves, then repeats build, capture, design-kit check and a fresh judge until every spec item passes. Use when the user wants our UI to look or work like another app's, asks for UI references or inspiration, mentions Mobbin, or wants a screen compared with competitors.
---

# UI references

Make one of our screens work and read like a reference product's, built only from our design kit. The **spec** is the target, a fresh **judge** marks each spec item pass or fail every round, and the **kit gate** keeps every colour and font ours. The climb ends when the spec passes, not when the builder feels done.

`<skill>` is this folder, `~/.claude/skills/ui-references`. `<board>` is `<workspace>/ui-references/<feature>/`, outside any git repo, where `<workspace>` is the folder that holds the project's repo. The screen library lives in `~/.design-library` (override with `$DESIGN_LIBRARY`), shared across projects. Run `node <skill>/library.mjs` with no arguments for every command.

## Rules

- Borrow structure and behaviour: layout, hierarchy, density, interaction, states. The kit supplies colour, type, radius, icons and copy. The reference's logo, illustrations, icons and wording stay out.
- DESIGN.md and PRODUCT.md are the authority. A spec item the kit can't express is the user's decision, and either file changes only on an explicit yes.
- The builder never judges its own round. Every round gets a new judge subagent on the highest model tier available.
- Ask before any logged-in capture. Use demo or test workspaces, never other people's private data. `--run` (clicks, opening menus) is for our own dev server only. With `--logged-in` the script runs it only on localhost.
- Climb captures go to `<board>` with `--out`. Only reference screens go into the shared library.

## Steps

### 1. Scope

Read PRODUCT.md and DESIGN.md, and find the **kit files**: DESIGN.md plus whatever defines the tokens (tokens CSS, Tailwind theme, the component library's theme). Name the target page on the dev server, the reference product, and the regions R1, R2…: one per component the user cares about, each with a CSS selector on our page. Seed the dev server with realistic demo data, since the judge compares filled screens.

Done when: the kit files, target URL, reference product and every region's selector are written down.

### 2. References

Per region, collect the reference's version of the component, cheapest first:

- `search <app> <flow>` reuses what the library has.
- `capture <url> --app A --flow F --selector <css>` for public pages. `--phone` gives 390×844 at 2×.
- Behind a login: `login <url>` once. The user signs in and quits that Chrome, then you run `capture ... --logged-in`.
- States behind a click (an open menu, an empty list, an error): help-centre images through `add <image URL> --app A --flow F --platform web --source <article>`, or ask the user for screenshots and `add <files> --app A --flow F --platform P`.
- `appstore "<name>"` last, because store screenshots are staged marketing. Mark them `"marketing": true` on the board.

When the user named no reference for a region, collect 2 or 3 candidates and let them pick one per region from the board. Run `mono` on every reference image. Capture ours as the baseline: `capture <dev url> --out <board>/r0/<R>.png --selector <css>`, then `mono` it.

Done when: every region has a picked reference with colour and grayscale images, and our baseline is captured the same way.

### 3. Spec

From each picked reference, write items T1, T2…, each one checkable sentence of 20 words or fewer about what a judge can see in a grayscale capture: arrangement, what is visible by default versus behind a click, density and spacing rhythm, hierarchy, the state shown, and how the copy is structured (not the wording). Colour, font and brand are left out, because the kit gate owns them. An item that needs a token the kit lacks says so in its text, and approving it means approving that DESIGN.md change.

Copy [template.html](template.html) to `<board>/index.html`, replace only the JSON in `<script id="data">`, run `node <skill>/check.mjs <board>/index.html` until it prints `ok`, and open it. Ask the user to answer per item, for example `keep T1 T3, reject T2 because…`. When a rejection states a preference that will recur ("no boxes inside boxes"), offer it as a DESIGN.md rule and add it to `taste` once they say yes.

When the user can't answer (an unattended run), stop here and hand back the board. The climb starts only from an approved spec.

Done when: every spec item is approved or rejected.

### 4. Climb

Repeat rounds n = 1, 2…:

1. **Build.** Change our code toward the failing items, using kit tokens and existing components only. Keep passing items passing.
2. **Capture.** For each region: `capture <dev url> --out <board>/r<n>/<R>.png --selector <css>`, with the same viewport, data and state as the reference, then `mono` it.
3. **Kit gate.** `tokens <dev url> --from <kit files>`, with the same `--selector`, `--phone`, `--run` and `--logged-in` as the capture, prints every rendered colour and font the kit doesn't contain, including a kit font that never loaded. Fix them before judging. Record the count as `offKit`. Browser-default controls count as off-kit, because they are unstyled.
4. **Checks.** Run the project's build, lint and tests. A regression fails the round.
5. **Judge.** Dispatch a new subagent. Give it the approved items, the reference grayscale crops, this round's grayscale crops of ours, our colour crops, and the kit files. Leave out the builder's notes and earlier verdicts. Brief it: judge structure and behaviour against each item, mark pass only when the capture shows it, mark fail when unsure, and give each verdict a reason of 15 words or fewer.
6. **Record.** Add the round to the board (`shots`, `results`, `offKit`) and run `check.mjs`.

Stop at the first of:
- **Summit:** every approved item passes with `offKit` 0, and a second new judge confirms it on the same captures.
- **Plateau:** the pass count hasn't risen for 2 rounds. Report the stuck items and what blocks each.
- **Cap:** 6 rounds.

Done when: one stop condition is met and the board shows every round.

### 5. Hand back

Open the board. Report the pass count, the last `offKit`, the stuck items, and the files changed. The user reviews in colour: the judge saw only structure, so colour and taste are theirs to call. Run `library.mjs gallery` to refresh the library's index.

## Board data

- **Top level:** `title`, `goal`, `target` `{app, url}`, `kit[]` (file paths), `taste[]`, `regions[]`, `spec[]`, `rounds[]`.
- **Region:** `id`, `name`, `selector`, `picked` (an app in `refs`), `refs[]` of `{app, src, mono, source, marketing?}`, and `ours` `{src, mono}` (the baseline).
- **Spec item:** `id`, `region`, `item`, `from`, `status` (`proposed`, `approved` or `rejected`), and `reason` when rejected.
- **Round:** `n`, `shots` `{<region id>: {src, mono}}`, `results` `{<item id>: {pass, why}}` for every approved item, and `offKit`.

Image `src` takes absolute local paths. Remote URLs are rejected so the board stays local. The template's JSON is a worked example.
