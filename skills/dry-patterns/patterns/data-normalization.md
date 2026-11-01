# Data Normalization

Store each fact once and reference it by key, so an update changes one row instead of every copy.

Refs: https://en.wikipedia.org/wiki/Database_normalization
Example: [examples/data-normalization.ts](../examples/data-normalization.ts)

**Principle** — Edgar F. Codd introduced normalization (first normal form in 1970, second and third in 1971) to remove redundancy and the insertion, update and deletion anomalies it causes. It is DRY for stored data: the customer's email belongs to the customer, not to each order.

**Violation signals** — Columns or fields copied from a parent onto children (`customerEmail` on every order). Update code that loops over many rows to change one fact (`changeEmailFlat` touches two rows). JSON documents that embed copies of shared records.

**Fix** — Split the repeated fact into its own table or map keyed by id, keep only the foreign key on the child, and join on read. In the example `customers` holds the email, `orders` keep `customerId`, and `emailForOrder()` does the lookup. Facts that must stay as they were at the time, such as the address on a shipped invoice, are snapshots, not duplicates: store them on purpose and name them so.

**When not to apply** — Read-heavy systems and analytics often denormalize on purpose (materialized views, star schemas). Let the database maintain the copy (materialized or indexed views) instead of application code. Measure the read problem first.

**Related** — **Flyweight** (`gof-patterns-typescript/patterns/flyweight.md`) for sharing one immutable copy in memory; **Proxy** (`gof-patterns-typescript/patterns/proxy.md`) for a cache in front of normalized reads; [`single-source-of-truth`](single-source-of-truth.md); [`premature-optimization`](../../kiss-patterns/patterns/premature-optimization.md) before denormalizing.
