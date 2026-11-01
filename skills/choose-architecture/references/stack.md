# House stack rules

The owner's own defaults for language, runtime, framework and tooling per deployable. Each rule names the force that selects it. These are house opinions, not book rules: quote them as "house rule" in the decision record.

## Decision rules

- **Go** for a backend deployable where the step 5 capacity arithmetic shows CPU-bound or highly parallel work that one Bun process cannot carry at the NFR's p99 target: a matching engine, bulk signing or verification, heavy stream processing. Finance at that load is the clearest case. When the bottleneck is an outside rate limit, the database or a wallet's transaction ordering, the language does not move it, and this rule does not apply.
- **Next.js** for a frontend whose Capability force names public, logged-out visitors in large numbers: pages anyone can open without a login, where search ranking and link previews matter.
- **TypeScript backend**: run on **Bun**, structure services, errors, dependencies, retries and concurrency with **Effect**.
- **Python backend**: **FastAPI**, linted and formatted with **ruff** at its widest setting: `select = ["ALL"]`, ignoring only rules that conflict with the ruff formatter or with each other, each ignore commented with its reason.
- **TypeScript toolchain** for every TS deployable: **Vite+** for dev, build and test, **oxlint** for linting. A Next.js app builds with Next's own toolchain and still lints with oxlint.

## When a rule meets a force

- A house rule is the default. When the Team force says nobody on the team runs that stack and the Time force leaves no room to learn it, record both views and the force that settles it, the same way as an advisory disagreement.
- A deployable no rule covers: pick by the Team force (what the team already runs in production) and label the choice "not a house rule".
