# GitHub design-skill research

Research date: 2026-11-04. Request type: comprehensive research. Scope: reference-driven polish of crypto, fintech, banking and AI product interfaces; calm, minimal, responsive interaction; preserve the product's own design kit; no `/goal`; no mandatory reviewer count or subscriptions.

This is a source/workflow comparison, not a visual benchmark. Actual skill entrypoints and selected supporting files were inspected. No candidate was installed or run, and no rendered winner is claimed. Repository popularity was not used as a proxy for design quality.

## Direct answer

The closest workflow match is **Mobbin's official `redesign-screen`**. The user has now chosen it as the substantial source for our adaptation, with public/local retrieval replacing the subscription service. Our existing skill contributes local capture/library tooling, explicit spec tracking, kit checks and round history. Other candidates below remain comparison evidence; they are not proposed wholesale imports.

The source comparison supports that fit; actual output quality still needs a controlled build comparison. Removing a paid service preserves the method but cannot promise the same coverage of authenticated product flows.

## Candidates compared

| Candidate | Evidence inspected | Most useful contribution | Why it is not a complete replacement |
|---|---|---|---|
| [Mobbin `redesign-screen`](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/SKILL.md) | Skill; taste and variation references; licence | Trace each change to an observed product screen; preserve baseline; show before/after | Stops without Mobbin; scoping and explore mode require user answers; targeted pass caps problems at five |
| [Refero `refero-design`](https://github.com/referodesign/refero_skill/blob/2382e518f90096df607196b9a635da2d1bc142f9/skills/refero-design/SKILL.md) | Skill; README; licence | Separate visual direction, screen patterns and flows; lock one primary direction | Styles currently describe marketing/product pages; styles-first routing is less direct for existing finance tools |
| [Community `mobbin-design`](https://github.com/notsointresting/mobbin-design/blob/4fbd49cf577c871cd2bf27e6baea5f4053341cd1/skills/mobbin-design/SKILL.md) | Skill; README; licence and attribution notice | Image-first research, separate direction/pattern searches, reference lock and decision ledger | Mandatory signature motion; broad skill-priority assertions; unofficial MCP descriptions can drift |
| [Impeccable 4.8.0](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/.agents/skills/impeccable/SKILL.md) | Skill; Operate and critique references; licence/notice | Task-oriented product UI with precise hierarchy, restraint and meaningful states | Full workflow includes its binary/context infrastructure; critique mandates isolated subagents when available |
| [Taste Skill v2](https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill/SKILL.md) | Skill; app-screen reference; licence | Distinct app/page routes; real-browser inspection; honest, useful data density | Direction-dealing scripts and house rules are substantial; its stated app corpus is desktop-focused and unnamed |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/713eef51b04efc98d6fa565323b495f7c9c89fd4/.claude/skills/ui-ux-pro-max/SKILL.md) | Skill; manifest; licence | Searchable product, accessibility, chart and stack guidance | A guidance database rather than an observed-screen research workflow |
| [Anthropic `frontend-design`](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design/SKILL.md) | Skill and skill-local licence | Compact brief-specific art direction, restraint and useful UI wording | Does not supply reference retrieval, durable comparison board or strong verification mechanics |
| [Vercel `web-design-guidelines`](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/web-design-guidelines/SKILL.md) | Skill; actual guideline source; repository licence declarations | Concrete keyboard, focus, form, motion and rendering checks | Code review supplement, not design direction or reference discovery |

## What to reuse and what to leave out

### Official Mobbin

Its `Ground rules`, `Scope the target`, `Freeze the baseline`, `Search and lock references`, and `Plan the moves` are the closest reusable backbone. A reference must visibly demonstrate the decision; multiple captures of one app do not become multiple independent precedents. The workflow preserves domain, design system, content and boundaries. Keep this evidence discipline and its per-change explanation. [Source](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/SKILL.md#ground-rules)

The supporting [taste rules](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/references/taste.md) make useful choices for this user's minimal aesthetic: every addition answers a problem, new components follow existing siblings, and preserving empty space is legitimate. [Variations](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/references/variations.md) provides a concrete side-by-side exploration method. For our adaptation, explicit user constraints should choose whether to explore or proceed; disconnected Mobbin should fall back to supplied captures/public evidence, not stop all work.

### Refero and the community Mobbin adaptation

Refero's reusable sections are `Non-Negotiables`, `Workflow Routing` and its research/synthesis steps: choose one dominant source, preserve its defining choices, attach concrete decisions to evidence, and inspect the final rendering. It explicitly supports using bundled references when MCP is unavailable. Its own description limits styles to web marketing/product pages, even though it still advises styles-first for app work. Prefer app screens and flows for this use case. [Source](https://github.com/referodesign/refero_skill/blob/2382e518f90096df607196b9a635da2d1bc142f9/skills/refero-design/SKILL.md)

The community adaptation adds a particularly useful distinction: search named-product visual direction separately from the literal component/state. It requires looking at returned images rather than extrapolating from metadata. Its reference lock records primary source, preserved traits, narrow secondary borrowing and rejected defaults. These are worth adapting. Its mandatory motion/signature interaction would work against some calm finance and tool surfaces; retain purposeful interaction feedback without requiring spectacle. Do not copy its assertion that it outranks all other design skills. [Source](https://github.com/notsointresting/mobbin-design/blob/4fbd49cf577c871cd2bf27e6baea5f4053341cd1/skills/mobbin-design/SKILL.md)

### Craft supplements

**Impeccable:** reuse the distinction between Operate surfaces and marketing/experience surfaces. Its [Operate reference](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/.agents/skills/impeccable/reference/operate.md) values familiar affordances, restrained accents, coherent type, structural responsiveness and full component states. This directly fits financial tools and a Herdr-like workspace. Its [critique protocol](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/.agents/skills/impeccable/reference/critique.md) requires two isolated assessments when subagents exist; do not import that requirement when the user's goal is to avoid manufactured reviewer diversity.

**Taste Skill:** borrow the app/marketing distinction and requirement that data, primary controls and requested content remain useful after decorative material is removed. The [app-screen chapter](https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill/references/app-screens.md) explicitly warns that quiet but thin screens lost its own blind comparisons. That is useful caution against mistaking minimalism for quality. The author's study claims are not independently verified; unnamed desktop examples are not a substitute for our named, current reference catalogue. Avoid importing random direction selection or fixed visual rules wholesale into an existing brand.

**UI UX Pro Max:** reuse semantic, outcome-specific search queries and verification of returned relevance, especially for accessibility, chart readability and mobile controls. Its [query contract](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/713eef51b04efc98d6fa565323b495f7c9c89fd4/.claude/skills/ui-ux-pro-max/SKILL.md#query-contract) is better than selecting an industry palette and treating that as research. Existing kit authority should override a newly generated design system. No need to import all its data/scripts merely to add a checklist.

**Anthropic:** its [restraint/self-critique and writing sections](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design/SKILL.md) offer compact guidance for intentional hierarchy, sparse motion, consistent action names and useful empty/error copy. Use as craft principles, not a new authority over the app's existing tokens.

**Vercel:** its [guidelines](https://github.com/vercel-labs/web-interface-guidelines/blob/434b7f91364665f2f733b310ec54809bf8f37937/command.md) give observable checks: visible focus, semantic controls, usable forms, interruptible motion, reduced-motion support, robust content handling and tabular numbers. The separate [README](https://github.com/vercel-labs/web-interface-guidelines/blob/434b7f91364665f2f733b310ec54809bf8f37937/README.md) labels Vercel-specific preferences. Do not promote those into universal brand rules, especially its currency display preference for crypto precision.

## Side-by-side fit with our baseline

This compares the previously installed three-reviewer version supplied in the session, before the current revision.

| Need | Our baseline | Official Mobbin | Suggested synthesis |
|---|---|---|---|
| Preserve the current product/brand | Kit gate and approval boundary | Detailed Preserve list | Keep both |
| Explain why a layout changed | Spec traced to reference product | Specific visible decision per problem | Add screen-level decision evidence |
| Find useful references | Local library/public capture | Screens, flows, sections, collections | Public/local by default; optional connected services |
| Track iterations | Board and round folders | Before/after report | Keep the board, add concise decision ledger |
| Operate with one subscription | Blocked by fixed council | No mandatory council | Remove fixed count and subscription gate |
| Avoid correlated model votes | Three fresh agents can still be one model | No numerical model consensus | Record actual provider/model; distinct-provider review optional |
| Demonstrate a smooth interaction | Interaction checks, screenshot emphasis | Job walk/render checks | Add observed interaction/video evidence when motion matters |
| Broad domain reference catalogue | Not present | Searches live; no fixed list | Curated, tagged catalogue as search starting points |
| Prove visual superiority | Uncalibrated 9/10 threshold | No controlled benchmark supplied | Run equal-input comparison before declaring a winner |

## Proposed comparison experiment — not executed

Use one representative financial screen and one AI workspace screen with a frozen source commit, realistic deterministic demo data, the same route/state/viewport list and identical task constraints. Run our revised workflow and the official Mobbin workflow in separate disposable branches with the same available builder model, equal context and equal time budgets. Holding the builder model constant helps isolate the workflow rather than confounding model and skill.

Capture both outputs before showing either to the evaluator. Hide workflow labels and alternate their left/right placement. Compare task completion, preservation of required content, hierarchy/density, brand consistency, keyboard/accessibility checks, mobile handling and observed motion. Record specific tradeoffs and the user's preference; a distinct-provider model can add a second opinion if available. Do not turn same-model repetitions into votes or claim the experiment ran without its artifacts.

The final merged version should take observed strengths from both builds. This research only establishes plausible ingredients; it does not establish that combining more instructions improves output.

## Versions and reuse conditions

All hashes below were resolved from public Git remotes on the research date. Some source text was read at the moving branch and paired with that contemporaneous HEAD; pins are supplied for reproduction. Search snippets were used for discovery only. The `tasteskill/tasteskill` mirror was excluded after identifying `Leonxlnx/taste-skill` as the inspected upstream.

| Repository | Pinned HEAD | Licence evidence |
|---|---|---|
| mobbin/skills | `79124d92763f6e85107386227a96bbc40479710e` | [MIT, Copyright 2026 Mobbin](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/LICENSE) |
| referodesign/refero_skill | `2382e518f90096df607196b9a635da2d1bc142f9` (`master`) | [MIT, Copyright 2026 Refero](https://github.com/referodesign/refero_skill/blob/2382e518f90096df607196b9a635da2d1bc142f9/LICENSE) |
| notsointresting/mobbin-design | `4fbd49cf577c871cd2bf27e6baea5f4053341cd1` | [MIT, Sahil and Refero](https://github.com/notsointresting/mobbin-design/blob/4fbd49cf577c871cd2bf27e6baea5f4053341cd1/LICENSE); [per-file NOTICE](https://github.com/notsointresting/mobbin-design/blob/4fbd49cf577c871cd2bf27e6baea5f4053341cd1/NOTICE), both fetched directly after web-cache misses |
| pbakaus/impeccable | `9fadc41729c38fd47d7ae622b501558653f9d2e9` | [Apache-2.0](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/LICENSE); [third-party NOTICE](https://github.com/pbakaus/impeccable/blob/9fadc41729c38fd47d7ae622b501558653f9d2e9/NOTICE.md) |
| Leonxlnx/taste-skill | `12af471f627f866411b4bd785b19646d3672784c` | [MIT, Copyright 2026 Leonxlnx](https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/LICENSE) |
| nextlevelbuilder/ui-ux-pro-max-skill | `713eef51b04efc98d6fa565323b495f7c9c89fd4` | [MIT, Copyright 2024 Next Level Builder](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/713eef51b04efc98d6fa565323b495f7c9c89fd4/LICENSE) |
| anthropics/skills | `ca45fc496a3436251f191354091d557da31c15b5` | [Frontend skill's own Apache-2.0 licence](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design/LICENSE.txt) |
| vercel-labs/agent-skills | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | [README states MIT](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/README.md#license); root LICENSE lookup returned 404 |
| vercel-labs/web-interface-guidelines | `434b7f91364665f2f733b310ec54809bf8f37937` | [Repository identifies MIT and exposes LICENSE](https://github.com/vercel-labs/web-interface-guidelines/tree/434b7f91364665f2f733b310ec54809bf8f37937) |

For copied substantial MIT material, retain its copyright and licence notice. For Apache-2.0 material, retain the licence, applicable attribution/NOTICE and mark modified files. The community Mobbin adaptation credits Refero for methodology and multiple craft reference files, so copying those needs that attribution chain too. These licence findings concern the skill text, not rights to redistribute screenshots or product assets. The current research file summarizes and links; it does not vendor those works.

## Limitations

- No rendered A/B test, provider-availability test, paid Mobbin/Refero session, or claim that any skill objectively produces the best design.
- If an optional reference service is used later, discover its actual tools and access then; no connector or account is required by this adaptation.
- The selected adaptation is official Mobbin methodology + our public/local retrieval and iteration tools. Other skills are contextual comparisons, not extra required layers.


## Porting the selected official skill without a subscription

The selected source is the official `redesign-screen` directory plus the relevant rules from official `search`. Keep Mobbin's MIT notice and a changed-file/provenance note. The `search` skill also invokes `best-practices`, and the report invokes `plain-writing`; replace those skill dependencies with local instructions or include adapted files, so no hidden invocation sends the user back to Mobbin.

Preserve the method: define the person's job, inspect the baseline, freeze scope/content/kit, research the actual screen or journey, choose one coherent direction, map each problem to a visible reference-backed change, render, compare and explain. Public reference retrieval should provide product name, source URL, local image path, platform, observed state, capture date and the exact visible decision. The paid service's `mobbin_url` becomes a provenance URL; `image_url` becomes an available local/downloaded asset. Never manufacture unseen flow steps.

The [official search rules](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/search/SKILL.md) transfer well: one screen/flow/section per query, only constraints justified by the task, search at the right level, inspect images, broaden weak queries, and distinguish same-domain precedent from structural borrowing. Do not transplant service-specific tool arguments, pagination, filters or platform availability into ordinary web search. Use official product/help/design pages, public demos, open-source running apps, supplied screenshots and the local library. Report missing authenticated states as evidence gaps.

Adapt the [scoping round](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/references/scoping-round.md) to the user's autonomous workflow: reuse already-specified scope and proceed on reversible choices; ask only when a substantive branch remains unresolved. Keep optional variants when useful. The [report format](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/references/report.md) supplies before/after evidence and per-change reference links, but its fixed closing menu and external `plain-writing` invocation need not become mandatory. Local screenshots and check results can remain durable artifacts.
