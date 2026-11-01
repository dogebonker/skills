# Boring Technology

Solve the problem with tools the team already runs and understands; spend new technology only where it buys a clear advantage.

Refs: https://mcfunley.com/choose-boring-technology
Example: [examples/boring-technology.py](../examples/boring-technology.py)

**Principle** — Dan McKinley's "Choose Boring Technology": a team has a few innovation tokens (he suggests about three), and each new database, language or service spends one. Mature tools fail in known ways; new ones bring unknown unknowns and lasting costs in monitoring, deployment and learning. His process: first ask how you would solve it with the current stack, write down why that stack is not enough, plan migration off whatever the new tool overlaps, and discuss it openly.

**Violation signals** — A new datastore or queue added for one feature. A home-made file format, parser or protocol (`JobLog` with tab-separated lines, full scans and no locking). Two tools in production doing the same job.

**Fix** — Reach for what is already installed and operated: `sqlite3` from the standard library replaces `JobLog` with `JobStore`, and gains atomic writes, a primary key and an upsert. When something new is justified, record the reason and the migration plan.

**When not to apply** — Boring is not frozen. Spend a token when the new tool is your product's advantage or the current stack has a documented limit you have hit.

**Related** — **Adapter** (`gof-patterns-typescript/patterns/adapter.md`) to wrap a tool behind your interface when a swap is planned; **Facade** (`gof-patterns-typescript/patterns/facade.md`); [`one-way-to-do-it`](one-way-to-do-it.md); [`generate-dont-repeat`](../../dry-patterns/patterns/generate-dont-repeat.md).
