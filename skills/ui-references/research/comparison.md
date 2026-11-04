# Our earlier skill, official Mobbin, and the local adaptation

Checked 2026-11-04. This compares instructions, tools and access requirements. It is not an executed visual benchmark or a claim that the outputs equal Mobbin's paid product.

## Decision

Use the official Mobbin design method as the workflow backbone, with our existing free/local capture and library tools as the retrieval and verification layer. The user explicitly selected this approach rather than buying Mobbin. The [eight-candidate research](github-skills.md) explains why it fits better than importing a broad frontend/craft skill.

Upstream is pinned and attributed in [UPSTREAM.md](../UPSTREAM.md). Both the skill and its supporting instructions are local. No Mobbin `best-practices`, `search` or `plain-writing` invocation remains in the execution path.

## Side by side

| Requirement | Earlier ui-references | Official Mobbin redesign-screen | Local adaptation |
| --- | --- | --- | --- |
| Diagnose the person's task before choosing a reference | Mostly page/region scope and spec | Explicit task walk and preservation | Retains task walk and adds caller/state checks |
| Work without Mobbin | Public/local library available | Stops when required search tools are absent | Public/local sources are the default |
| Reference matching | Reference picked per region | Exact decision, task, platform and structural direction | Adopts matching rules with backend-neutral queries and source records |
| Explain each change | Spec item points to reference product | Problem → observed decision → concrete move | Adds that chain to scope notes and acceptance criteria |
| Brand preservation | Colour/font kit scan | Preserve list plus component/theme rules | Keeps both; notes the scan does not prove semantic token roles |
| Real UI evidence | Captures and grayscale board | Actual screenshots and before/after presentation | Current colour/gray captures, interaction checks and source-linked report |
| Useful references across domains | No curated catalogue | Paid searchable product corpus | Free entry points grouped by task and platform; inspect screens at runtime |
| One available model/provider | Fixed council could block | No multi-provider council | No mandatory review count; optional distinct-provider critique only |
| Stop condition | Spec passes plus unanimous 9/10; builder could not finish alone | Render checks with limited correction rounds | Concrete scoped defects resolved, checks and evidence current; incomplete stops explicit |
| Comparison variants | Reference candidates on board | Up to three evidence-backed directions | Optional isolated variants using the same kit/data/state, without subscription tools |
| Complete a broad overhaul | Round history and PR delivery | Narrow target; five changes per pass | Named targets plus shared consistency checks; no silent loss of unfinished scope |
| Hidden dependencies | Local Node/Chrome helpers | Mobbin connector and linked skill dependencies | Local supporting files; alternative capture tools when needed |

Sources for official behaviours: [entrypoint](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/SKILL.md), [search](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/search/SKILL.md), [connection boundary](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/best-practices/SKILL.md), [variations](https://github.com/mobbin/skills/blob/79124d92763f6e85107386227a96bbc40479710e/skills/redesign-screen/references/variations.md).

## What the research supports

The adaptation has a better availability fit for this user: it can work with the current subscription/tools and preserves the earlier local board/token checks. Official Mobbin contributes a more concrete diagnosis and evidence method than the original spec-only approach. This is an instruction-level assessment. No scored screenshot comparison has been run.

The remaining gap is the corpus. A skill cannot recreate a maintained private library by describing it. Public demos, docs and videos can provide excellent examples, but they are less uniformly searchable and may omit signed-in, error or rare flow states. Brand lists reduce discovery cost; they do not eliminate the need to inspect and match the actual reference. Visual quality and motion remain unverified until a real target is built and exercised.

## A fair two-run comparison when there is a target

1. Freeze one source commit and choose a financial task or AI workspace with deterministic demo data, routes, states and viewports.
2. Give both branches the identical free reference evidence pack, brief, design kit and available builder model. Compare the earlier local workflow with this Mobbin-derived adaptation; label the two instructions accurately. An unmodified official Mobbin run without its connector cannot be claimed as a completed run.
3. Give both the same budget and freeze their resulting commits. Capture real BEFORE/AFTER outputs, relevant state transitions and check logs.
4. Show the outputs side by side without workflow labels. Ask which task is easier to scan and complete, where hierarchy and density are better, and what content or behaviours regressed. Measure or exercise responsiveness instead of judging it from still images.
5. Record concrete strengths and failures. If another provider at a comparable tier is available, its opinion can supplement the user's assessment; it is not required. Holding the builder model constant isolates workflow differences and is not a second independent reviewer vote.
6. Combine only demonstrated strengths, recapture the combined implementation and rerun affected checks. Do not report this proposed experiment as executed.

No product target was supplied for a build in this task. This turn researched and adapted the reusable skill; it did not redesign an app, run a live paid Mobbin session, or test product motion.
