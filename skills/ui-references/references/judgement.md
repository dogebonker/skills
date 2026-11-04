# Outperform the references

Run this after collecting references: judge the baseline, then judge each implementation round against the same two or three reference products. The target is for our app to score higher in both UI and UX than every comparator on the scoped task. The desired winner is an implementation target; verdicts come from observed evidence.

## Lock a fair comparison

Choose two or three distinct, relevant products with inspectable evidence for the same job, platform and audience. Include strong examples, not only disliked interfaces. User-supplied negative examples belong in the panel too, clearly labelled; they do not replace stronger benchmarks. A brand, design-system article or unrelated marketing page is not an application comparator.

Before changing code, record in `<board>/comparison.md`:

- the task, completion state, content complexity, platform, viewport, theme and test sequence;
- the reference products, exact source/version/date and saved captures or recordings;
- the rubric, applicable dimensions and evidence required to assess them;
- available tools and the review method: builder inspection, human feedback or an optional distinct-provider assessment.

Use a separate panel block for each scoped task and platform/viewport with comparable reference evidence. A whole-app comparison passes only when every required block passes; do not average a weak mobile flow into a stronger desktop result.

Keep the benchmark set and rubric fixed across rounds. A replacement requires a documented access or relevance reason and rescoring the baseline/current app against the revised set. Prefer gathering better evidence to replacing a difficult competitor. Keep amounts, fees, safety information, realistic list lengths and required controls comparable; an artificially empty screen is not a fair minimalism win.

## Use the strongest evidence the current model can inspect

Discover actual callable tools before choosing the method. Use complementary methods where they reveal different parts of the experience; there is no required vendor or capture package.

| Available capability | Compare | Evidence limit |
| --- | --- | --- |
| Computer/browser interaction | Execute the same safe task on our app and accessible reference demos. Check navigation, decisions, keyboard/focus, errors, recovery and scrolling. Save relevant state captures and action/result notes. | Record what was actually exercised. Do not make real financial transactions or change private accounts for a comparison. |
| Video recording and playback/inspection | Record equivalent journeys where permitted. Watch start, actions, transitions, interruption, completion and recovery; cite timestamps. | Recording a file without inspecting it proves nothing. Separate product behaviour from edits, network differences and recording speed. |
| Frame/image inspection but no video playback | Inspect ordered frames at named actions/timestamps and pair them with action logs where available. | Frames show sequence and layout; sampled frames alone do not establish smoothness, exact timing or input responsiveness. |
| Screenshot inspection | Compare matching states and viewports for hierarchy, typography, spacing, density, contrast and visible affordances. | This supports a visual verdict and limited state/affordance findings, not an end-to-end UX or motion win. |
| Source/DOM/accessibility-tree inspection | Check structure, semantic controls, labels, focus order and implementation alongside any visible evidence. | Source correctness alone does not establish appearance or experienced behaviour. |

Use live interaction when available and relevant; add inspected recordings when motion or transitions matter. A first-party video can supply reference evidence without login, with its limitations recorded. Evaluate each dimension using evidence available for **both** sides. Extra evidence from our app supports its own checks, not an invented score for the competitor.

If images cannot be inspected, continue permitted implementation checks and save artifacts for later visual assessment. If only screenshots are available, finish the visual comparison and explicitly leave the broader UX target unverified. Missing capabilities never justify fictional evidence, automatic zeros for competitors or manufactured reviewer agreement.

## Rubric and scores

Use these eight dimensions as separate ratings. Keep every row visible in the panel. Mark a dimension inapplicable only with a task-specific reason fixed before scoring; missing evidence is **not assessed**, not inapplicable. Fix any task-specific additions before the first scored round.

| Group | Dimension | What to judge |
| --- | --- | --- |
| UI | Typography | Typeface suitability within the brand, size/weight hierarchy, line height/length, text wrapping and numeric readability. |
| UI | Hierarchy | Primary action and key information lead; grouping and progressive disclosure make the next decision apparent. |
| UI | Spacing & density | Alignment, spacing rhythm, grouping, useful information per view, breathing room and realistic content at each viewport. |
| UI | Color & contrast | Semantic colour roles, text/control/focus contrast, restrained emphasis, state differentiation and light/dark legibility. |
| UI | Iconography | Recognisable meaning, coherent family/stroke/size, optical alignment and appropriate labels; icons or their deliberate absence serve the task. |
| UI | Consistency & polish | Components and states agree across screens; edges, truncation, responsive behaviour and small visual details feel finished. |
| UX | Clarity | Labels, navigation, next actions, amounts/fees and state/error/recovery messages let a person understand and complete the job. |
| UX | Animations & smoothness | Observed input feedback, transitions, scrolling, layout stability, interruption and reduced-motion behaviour support continuity without distracting motion. |

Score animations & smoothness from live interaction or inspected temporal evidence for both products. Still images cannot establish it, and sparse extracted frames alone cannot prove fluidity. A deliberately immediate, stable response can score well; decorative animation is not required. Keep keyboard/accessibility, task completion, state recovery and financial correctness as explicit pass/fail checks as well as evidence for the relevant ratings.

Score each evidenced dimension from 1–10 with the same anchors: **1** prevents the task or reading; **5** usable with material defects; **8** strong with concrete remaining issues; **9** polished with only minor issues; **10** no defect observed in the tested scope. Scores are ordinal design judgements, not calibrated measurements. Every score needs an artifact/state/timestamp and a short reason. Use **not assessed** for insufficient evidence, not a zero or an invented number.

Compute the UI and UX group scores as the mean of their applicable, fully evidenced dimensions; show the component ratings so an average cannot hide a regression. Do not compare group scores built from different dimension sets or mark a group complete while a required dimension is unassessed. Do not add precision unsupported by the component ratings.

A round meets the competitive target only when:

- our UI group score and UX group score are each **strictly higher** than those of **every** locked comparator;
- our score is at least as high on every individual applicable dimension, so a material weakness is not hidden by an overall average;
- no critical usability, accessibility, financial-information or functionality defect remains, and the normal spec/kit/project checks pass.

A tie is unfinished for the relevant group. When a reference is already at the scale ceiling, record the tie honestly; finding a weaker comparator or changing the scale does not establish superiority. Pairwise findings can guide improvement even when the full target remains unverified.

## The comparison/judgement panel

Persist the panel in `<board>/comparison.md` and update it after each round. Present it in the host's supported table/artifact surface; where a browser or computer-use surface can show a local report, render an equivalent HTML panel beside the existing image board. Do not require a separate app or paid canvas. Keep screenshots/videos linked beside the scores, with matching labels across the table and artifacts.

Use this shape, omitting Reference C only when there are two comparators:

| Group / dimension | Reference A | Reference B | Reference C | Our baseline | Our round n | Finding and evidence |
| --- | --- | --- | --- | --- | --- | --- |
| UI: typography | score | score | score | score | score | artifact/state and visible difference |
| UI: hierarchy | score | score | score | score | score | artifact/state and visible difference |
| UI: spacing & density | score | score | score | score | score | artifact/state and visible difference |
| UI: color & contrast | score | score | score | score | score | artifact/state and visible difference |
| UI: iconography | score | score | score | score | score | artifact/state and visible difference |
| UI: consistency & polish | score | score | score | score | score | artifact/state and visible difference |
| **UI group** | mean or not assessed | mean or not assessed | mean or not assessed | mean or not assessed | mean or not assessed | win/tie/loss/unverified per comparator |
| UX: clarity | score | score | score | score | score | action/result, state or timestamp |
| UX: animations & smoothness | score or not assessed | score or not assessed | score or not assessed | score or not assessed | score or not assessed | inspected interaction/recording and timestamp |
| **UX group** | mean or not assessed | mean or not assessed | mean or not assessed | mean or not assessed | mean or not assessed | win/tie/loss/unverified per comparator |

Include the capability/coverage note, benchmark source links, current commit or artifact identity, open defects and next fixes. Keep earlier rounds so improvement and regressions remain visible. Where practical, assess anonymous A/B/C/D artifact labels before revealing product identities; do not show the desired ranking or earlier scores during an optional fresh assessment. Never describe builder inspection as an independent review.

## Revise from the gaps

After each judgement, turn losses, ties, weak component ratings and observed defects into concrete implementation work. Fix those within the product's kit and Preserve list, recapture/re-exercise affected states, then update the panel. Improve the app rather than negotiating the scores. Re-evaluate all affected dimensions after a change; use reference scores again only while their version and evidence stay fixed.

Continue until the competitive target and ordinary checks pass. If an evidence gap, capability limit, authorization boundary or user limit prevents that, deliver the actual results and clearly mark the target unmet or unverified. Passing a visual subset is useful progress; it is not a claim that the overall UI/UX comparison passed.
