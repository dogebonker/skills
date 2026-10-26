---
name: explain-decisions
description: Teaches pending decision questions with the Feynman method on one local interactive HTML page, with a plain one-sentence version, a clickable walk-through of a real example under each option, a blast-radius heat grid, a quick quiz on the fact the choice hinges on, the pick with its drawback, and whose call it is. Then asks a short question that points to the page. Use before asking the user to choose between technical options (AskUserQuestion or a prose "A or B?") about code, tickets, data, rollout or other people's work, and when the user says they don't understand a question, lack the context, or asks what an option means.
---

# Explain decisions

The user is new to this codebase and team. "Q3: keep the denormalized total or drop it (Recommended)?" means nothing to them. Teach each decision with the Feynman method on an interactive page, then ask. Show, don't write: the page is steps to click, colors and a quiz, not paragraphs.

Skip the page for a name, wording, or yes/no the user plainly owns.

## Feynman pass, before writing anything

1. **Say it simply.** Write the decision in 30 words or fewer with no jargon. If you can't, you don't understand it yet. That's the gap.
2. **Close the gap at the source.** Read the code, ticket, PR and thread. Cite `file:line`. Find the owner (`git blame`, ticket reporter, CODEOWNERS). Never invent one.
3. **Walk one real example.** Pick one concrete case from this codebase (one file, one user, one request) and trace it in 3 to 5 steps: today, then under each option. Use real names and data, not an analogy.
4. **Find the fact it hinges on.** Prove it as far as is cheap (said, pointed at the line, ran it), using the `blast-radius` method. Turn it into a quiz question: if the user can answer it, they can decide.
5. **Cut.** `check.py` enforces a word limit on every field.

## Build and ask

1. Copy [template.html](template.html) to `<workspace>/decisions/<feature>/<NN>-<topic>.html` and replace only the JSON in `<script id="data">`. `<workspace>` is the folder that holds the repos (for example `~/Work/acme`), and `<feature>` is the ticket, such as `proj-123`. Never put pages inside a git repo. They're the user's own record of the feature, kept so they can defend it end to end. The page renders itself. The template's JSON is a worked example of every field.
2. Run `python3 ~/.claude/skills/explain-decisions/check.py <page>` and fix everything until it prints `ok`.
3. Run `open <page>` (or print the path where `open` doesn't exist), then AskUserQuestion with a plain question, option labels using the page's letters, and `Interactive explanation: <page path>` in the question text. AskUserQuestion takes at most 4 questions, so ask the first 4 and say the rest are on the page. The user can answer in the widget or paste the reply the page builds (`1A, 2B`).
4. When the user answers, write `answer` into that question's data, run `check.py` again, then run `python3 ~/.claude/skills/explain-decisions/index.py <feature folder>`. That rebuilds `index.html`, the feature's decision log, with each choice, who made it, when, and any caveat still unproven.
5. Rebuild the page whenever a question changes. Never send the user back to an older page.

## Data shape

- Top level: `title`, `goal`, `decided[]` (only answers that matter here), `terms{}`, `questions[]`. Every term becomes a hover or tap definition wherever it appears, so use terms instead of explaining inline.
- Each question:
  - `ask`, `ids` (tickets, PRs, files), `whyNow`, `ifSilent`.
  - `plain`: the Feynman sentence.
  - `views[]`: the walk-through, with `name`, `label`, `ref`, `ok`, `result`, and `flow[]` of `{t, d, state: ok|bad|new}`. The first view is today; one view per option follows.
  - `options[]`: `key`, `name`, and `radius` with `code`, `data`, `people`, `users`, `undo` and `cost`, each `{level 0-3, text}`.
  - `quiz[]`: `q`, `choices`, `answer` index, `explain`.
  - `pick`: `key`, `why`, `drawback`, `sure: said|line|ran`, and an optional `caveat` for an unproven fact the pick depends on.
  - `owner`: `who` (`You` when the user owns it, judged from the ticket assignee, not from who wrote the code), `why`, an optional `message` for the person to ask or tell, and `safeDefault`.
  - `evidence`: raw proof output, shown collapsed.
  - `answer`, added once decided: `key`, `by`, `date` (YYYY-MM-DD), and an optional `note` with follow-ups such as who to tell.

## Rules

- Label each view `Current — observed` (needs `ref`), `Current — not verified`, `Proposed` or `Illustrative`. Never pass off a plan as current behavior.
- Rate every blast-radius area for every option. 0 means nothing changes there. Include "keep things as they are" as an option when it's real.
- If the call belongs to someone else, say so, write their message, and give a safe default.
- Set `pick.sure` from the fact the pick depends on, not from a side fact you proved. An unproven condition goes in `caveat`.
- Cite `evidence` to where the output really came from.
- No session shorthand (X1, C3, L6) in page text. Exact identifiers go only in `ids` and `ref`.
- Use inline HTML, CSS and JS only, no network. Company code stays local, so don't publish the page unless asked.
