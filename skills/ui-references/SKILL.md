---
name: ui-references
description: Redesign or polish product UI from real shipped screens while preserving the product's own design kit. Adapts Mobbin's reference-driven method to public demos, official screenshots and a local library, with no paid service or multi-provider requirement. Use for UI polish, reference research, side-by-side directions, or crypto, fintech and AI product interface work.
---

# UI references

Improve the target using patterns visible in shipped products. Diagnose the user's task, preserve what works, find matching references, choose one coherent direction, connect every major change to evidence, and check the actual render. After collecting references, benchmark our baseline and each revision against two or three comparable products, iterating until our app wins the scoped UI and UX comparison. The product keeps its own brand, content and design system.

This is a local adaptation of Mobbin's official MIT-licensed design skills, not a replacement for its private screenshot corpus. [UPSTREAM.md](UPSTREAM.md) records the source version, changes and licence. No Mobbin subscription, reference-service account, extra model provider, canvas subscription or `/goal` runtime is required.

`<skill>` is this folder. `<board>` is `<workspace>/ui-references/<feature>/`, outside the product repo, where `<workspace>` holds that repo. Reference images live in `~/.design-library` (override `$DESIGN_LIBRARY`). Run `node <skill>/library.mjs` without arguments for command help. The helpers use Node 22+ and installed Chrome; an available browser/capture tool can substitute.

## Evidence and scope

- Inspect the actual target before searching. Distinguish a whole screen, a component, a marketing section and a multi-step flow. A whole-app request is a sequence of named targets plus a final consistency pass.
- A cited reference is an image or interaction you inspected, with a source link and a recorded state/platform. Search snippets, brand reputation and memory are discovery leads. Two products support a precedent; one is an example. A judgement call is labelled as judgement.
- Match the job before the look. A cross-domain example supplies a bounded structural idea, not financial behaviour or the product's identity. Reference colour, logos, copy and example data are not imported into our brand.
- PRODUCT.md, DESIGN.md, existing tokens/components and the current brief govern the implementation. Record gaps when documents are absent. Change product behaviour, kit definitions or dependencies only within the user's authorization.
- Resolve ordinary reversible layout choices directly. Ask only when missing information changes the target, product behaviour, design authority or access. Reference-only research does not authorize implementation or publication.
- Preserve real financial information and controls. Never hide fees, units, network/destination, precision, warnings or confirmations merely to make a money screen quieter.
- No fixed council, numeric consensus or repeated same-model review is required. Inspect the render with the tools available. Optional additional critique uses genuinely distinct available providers at a comparable capability tier; report actual coverage, without treating missing subscriptions as a blocker.
- Use public or demo reference evidence. Ask before accessing a logged-in reference product; never collect other people's private data. The helper's `--run` changes state only on our own dev server; with `--logged-in` it permits that only on localhost. Never send money, trade, sign or upload identity documents for reference research.

## Read when needed

| File | When |
| --- | --- |
| [references/search.md](references/search.md) | Before collecting external references; backend-neutral discovery, matching and attribution |
| [references/catalogue.md](references/catalogue.md) | Choosing candidate products; routes to finance/crypto and AI/native lists |
| [references/judgement.md](references/judgement.md) | After reference collection and every implementation round; capability-aware UI/UX benchmark panel |
| [references/taste.md](references/taste.md) | Before implementing and while checking the result |
| [references/variations.md](references/variations.md) | Comparing materially different directions |
| [references/report.md](references/report.md) | Delivering images, checks and per-change evidence |
| [research/github-skills.md](research/github-skills.md) | Reviewing alternative skills and reuse conditions |
| [research/comparison.md](research/comparison.md) | Comparing our earlier workflow, official Mobbin and this adaptation |

### 1. Scope the target and walk the job

Read the source: running code, a supplied screenshot, a design file or an accessible page. Write one line saying who arrives, what they need to do and what completion means. Enumerate the relevant loading, populated, empty, error, disabled, overflow and narrow states. An image proves only its pictured state; a crop says nothing about content outside its frame.

Walk the task and record concrete problems:

1. Is the first step clear, with a clear primary action for the current decision?
2. Is the information needed for each decision beside it?
3. Are the necessary content and controls present?
4. Do labels, values, totals and actions agree?
5. Can the person complete the task, recover, or understand why they cannot in each reachable state?
6. Do platform conventions, readable text, contrast, target size and keyboard/focus behaviour hold?

Rank observed problems by what they block, starting with the user's complaints. “Premium” or “minimal” becomes a visible question about hierarchy, density, spacing or treatment; it is not permission to add decoration.

Name each region R1, R2… by file/component and CSS selector when applicable, what it includes and what remains outside it. Inspect callers of shared components and check other affected screens. A scoped shared change can proceed with those checks; a broader redesign needs explicit scope.

Default to a targeted implementation for a clear improvement request. Use [variations](references/variations.md) for requested alternatives or unresolved structural directions. Record the target, assumptions, viewport/state list and authorization in `<board>/scope.md`. An image-only job produces an explicitly labelled mockup, not a claim that application code was changed.

Done when: the job, target boundaries, problem list, source form and relevant states are explicit.

### 2. Freeze what must survive

Record the Preserve list: domain; theme and kit files; real copy/data/units/routes; functionality and content; everything outside the target; and the user's explicit constraints. Keep an actual baseline capture, never a reconstruction presented as BEFORE. For code, use a dedicated branch or isolated checkout without disturbing unrelated edits.

For a code source, seed our dev server with realistic deterministic demo data. Record desktop and mobile viewports and applicable themes. For a running web target, capture baseline regions with `capture <dev url> --out <board>/r0/<R>.png --selector <css>` and full screens with `capture <dev url> --out <board>/r0/<screen>.png --full`; add `--phone` for 390×844 mobile. Desktop is 1440×900. `--full` caps height at 8000px; capture additional scroll positions if needed. Create grayscale versions with `mono <image...>`.

Done when: the baseline and Preserve list can detect content loss, brand drift and changes outside scope.

### 3. Find matching screens and choose a direction

Follow [search.md](references/search.md), using the local library and inspectable public sources. The [catalogue](references/catalogue.md) is a candidate list, not evidence that a specific current screen is good. User-supplied collections or screenshots take priority; stay inside an explicitly exclusive collection.

Search by screen/job and state, and use walkthroughs for sequencing. Examine selected images at readable size. Group relevant examples by the structural solution they demonstrate; choose one coherent direction for the target. Use a few anchor screens and a secondary pool for bounded details. Record rejected examples and why they do not fit. A missing paid connector never blocks public/local research.

For each selected example, save product, source URL, local image, platform/state, checked date and **take/leave**: the exact decision to adopt and the brand/content/irrelevant behaviour to leave behind. Several images of one product still count as one product. Preserve a primary direction instead of averaging incompatible solutions. A sparse result set is a coverage limit, not proof that every product uses the same pattern.

When no external screen is usable, a region may name its own baseline `Existing product` in `refs` for preservation only. Record the missing external coverage explicitly; this is best effort, not an external reference match.

Done when: the chosen direction has inspectable evidence and every major proposed decision has a source, user requirement or explicitly labelled product judgement.

### 4. Lock the benchmark and judge the baseline

Follow [judgement.md](references/judgement.md). Select two or three meaningful reference products, freeze comparable tasks/states and the eight-dimension rubric (typography, hierarchy, spacing & density, color & contrast, iconography, consistency & polish, clarity, animations & smoothness), then score the baseline and references from actual evidence. Save the comparison/judgement panel in `<board>/comparison.md` with source/artifact links and review coverage.

Use whatever the current model can actually operate and inspect: computer/browser interaction, video, ordered frames, screenshots and semantic inspection as applicable. Compare like evidence for each dimension. Screenshot-only access permits a visual comparison; it does not establish a complete UX or motion win. No additional provider subscription or fixed council is required.

The target is for our app's UI and UX group scores each to exceed every comparator, with no lower individual dimension score or critical defect. Keep the evidence and ratings honest: a tie, loss or unassessed required dimension remains work. Missing access or capabilities limits the claim; it does not lower the competitors' scores. For reference-only research, deliver the benchmark plan without implying an implementation was authorized.

Done when: the comparator set, rubric, capability coverage and baseline panel are recorded, including unassessed dimensions.

### 5. Plan the changes

Write one move per problem in `<board>/scope.md`: problem → decision → exact supporting screen/interaction → what changes → what must remain → visible acceptance criterion. The reference must show the decision, not merely contain the same kind of element. Record judgement separately for unsupported placement, wording or domain details. Avoid stock badges, panels, icons, new copy or motion without a problem to solve.

Keep all required content and controls: rearrange and regroup before removing. A move needing new behaviour or a theme change goes through the existing authorization boundary. Work in small verifiable groups, carrying unfinished in-scope problems forward; a report-size limit never silently drops the rest of an overhaul.

Translate visible requirements into T1, T2… (20 words or fewer), each tied to a region and source. Mark items covered by the request and kit `approved`; record rejected items with reasons. Resolve materially new decisions before dependent work. For code runs, copy [template.html](template.html) to `<board>/index.html`, replace only `<script id="data">`, and run `node <skill>/check.mjs <board>/index.html` until `ok`.

Done when: each planned change answers a problem, respects Preserve and has a checkable result.

### 6. Apply, capture and iterate

Read [taste.md](references/taste.md). Implement with the existing components, tokens and platform conventions. Keep real controls wired to real state; add no speculative functionality. A supplied design file gets a new frame only if the connected tool can write; otherwise deliver a labelled mockup/capture.

The code/dev-server loop below applies when an implementation can run. For an image or design-file-only source, use available export/capture tools and visual kit comparison, record runtime checks as unavailable, and deliver a labelled design artifact rather than a verified application. Use the board for code runs; an image-only before/after can be delivered directly without inventing a dev URL or token-check result.

For each code round n:

1. Implement the failing moves and keep passing requirements intact.
2. Capture regions and full screens into `<board>/r<n>/` with the baseline's viewports, data, themes and states. Generate grayscale crops for structure; inspect full colour for typography, hierarchy, spacing & density, color & contrast, iconography, consistency & polish and visible clarity. Exercise interactions for clarity and animations & smoothness.
3. Run `tokens <dev url> --from <kit files>` with the capture's selector, phone and state options. Fix off-kit colours/fonts, unloaded fonts and browser-default controls. Record the total as `offKit`. The token scan is an allowlist aid; it does not prove correct semantic roles, spacing or accessibility. Check those in the actual render.
4. Exercise the task, keyboard navigation and relevant state transitions. Observe motion/scrolling directly or record it when smoothness matters; screenshots prove neither responsiveness nor animation quality. Respect reduced motion. Run available build, lint, typecheck and relevant tests.
5. Repeat the job walk and check Preserve. Record T-item verdicts, concrete defects, screenshot paths, test evidence and unavailable checks in `r<n>/review.md`. Add board `shots`, `results`, `offKit`; run `check.mjs`.
6. Update the [comparison/judgement panel](references/judgement.md) against the locked references. Turn losses, ties and unverified required dimensions into the next fixes or evidence-collection steps; score the actual current artifacts.

Iterate until approved items pass, offKit is 0, required checks pass, material scoped defects are resolved, and the competitive UI/UX target in judgement.md passes against every locked reference. An evidence-limited result is labelled partial/unverified rather than a completed competitive win. New changes require fresh captures and affected checks. A board-validator pass or a subjective 9/10 is not proof of design quality. If a direction stalls, revisit it with the evidence rather than repeating the same ineffective edits. Stop incomplete for a real blocker, user limit or cancellation, preserving the artifacts and unmet criteria.

Done when: the current implementation and current evidence agree on what passed and what remains.

### 7. Show the result and deliver

Follow [report.md](references/report.md): show real BEFORE/AFTER captures at matching scale, explain each visible change against its source, and report checks, benchmark scores/rankings and evidence gaps. Link the comparison/judgement panel alongside the image board, including win/tie/loss/unverified per comparator. The board retains spec and round history; `review.md` carries the richer per-change and interaction evidence. Refresh `library.mjs gallery` after adding references.

For an authorized implementation overhaul, create/update a draft **UI polish overhaul** PR once reviewable work exists, following repository conventions and publication permissions. Keep iterating on that PR, attach reviewable screenshot evidence, and mark ready only after the scoped checks and competitive target pass; keep evidence-limited or incomplete comparisons draft. Never merge automatically. Research-only, comparison-only and image-only requests deliver their artifacts without a code PR. If publication is unavailable, finish local work and save the exact PR title/body and blocker.

Done when: the user has reviewable output, source links, actual verification results and a precise account of remaining work.

## Board data

The existing schema remains unchanged:

- Top level: `title`, `goal` (display text), `target` `{app,url}`, `kit[]`, `taste[]`, `regions[]`, `spec[]`, `rounds[]`.
- Region: `id`, `name`, `selector`, `picked` (an app in `refs`), `refs[]` `{app,src,mono,source,marketing?}`, `ours` `{src,mono}`.
- Spec item: `id`, `region`, `item`, `from`, `status` (`proposed`, `approved`, `rejected`), `reason` when rejected.
- Round: `n`, `shots` `{<region>: {src,mono}}`, `results` `{<approved item>: {pass,why}}`, `offKit`. Reasons are 15 words or fewer.

Use local image paths; remote board URLs are rejected. Full-page captures, reference provenance, move tables, interaction evidence and review notes live beside the board. The template is a worked example, not a claim that the depicted interactions were tested.
