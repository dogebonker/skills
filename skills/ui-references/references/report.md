# Deliver evidence the user can inspect

Adapted from Mobbin's MIT-licensed report and before/after guidance. See [upstream notices](../UPSTREAM.md).

Lead with the result and the actual before/after images or board link. Use matching viewport, data, state, theme and crop; compare changes in the target rather than unrelated surroundings. AFTER comes from the current implementation or an explicitly labelled mockup. Do not redraw a reconstruction and call it the baseline.

For each meaningful change, give one short explanation and a source link that shows that particular decision. State unsupported placement/wording as judgement. Do not cite an attractive screenshot merely because it contains the same component. Separate observed outcomes from intended benefits; a design pass does not establish conversion or retention gains.

Keep the reply concise, while preserving the detailed evidence in the local board and review files. Include:

- what visibly changed and how it answers the scoped problem;
- the before/after artifact and source links;
- the [comparison/judgement panel](judgement.md), all eight separate dimension ratings, UI/UX group scores and win/tie/loss/unverified against each locked reference;
- validation performed, remaining defects and evidence gaps, including the limits of screenshot-only or sampled-video inspection;
- actual reviewer coverage only if additional critique ran;
- changed files and a PR link when a code PR belongs to the authorized task.

Do not require a closing menu or another confirmation after ordinary completed work. Research, variants and image-only work can finish with their own artifacts. An inaccessible source or unavailable capture is stated explicitly; never imply it was inspected.

The current board already shows reference, baseline and latest region captures together. Keep using it; full-page pairs and interaction recordings can remain next to it with links in the report. Check that images and fonts loaded and that the delivered comparison is readable. If a remote reviewer needs access, use the repository's supported artifact mechanism; absolute local paths alone are not remotely accessible. Do not publish third-party/private screenshot libraries as PR evidence.
