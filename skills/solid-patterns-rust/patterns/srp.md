# Single Responsibility (SRP)

Keep together the code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.rs](../examples/srp.rs)

**Principle** — Martin defines a responsibility as a reason to change, and later as the group of people who request it; his `Employee` example mixes pay rules (finance), hour reports (operations) and storage (platform). In Rust the unit is the module and the `impl` block, not a class. A struct can stay plain data while separate modules own the behavior each group changes.

**Violation signals** — One `impl` block whose methods belong to unrelated owners, as `Employee` has `pay_cents`, `hours_report` and `to_row`. A `mod utils` or `helpers.rs` imported everywhere.

**Fix** — Keep `Employee` as data and move each job into its module: `payroll::pay_cents`, `reporting::hours_line`, `storage::to_row`. In a crate, each module becomes its own file, and visibility (`pub(crate)`) marks what crosses the boundary. Trait impls for serialization can live in the storage module, next to the format they serve.

**When not to apply** — A module per function, or a trait per method, for code one team owns and changes together. Small structs with a few cohesive methods are fine. Split when two owners actually edit the same code, not in advance.

**Related** — **Facade** (`gof-patterns-rust/patterns/facade.md`) for one entry point over the split modules; **Strategy** (`gof-patterns-rust/patterns/strategy.md`) for passing a rule in as a closure; **ISP** ([isp.md](isp.md)) for the same split seen from callers; **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`) for the overuse case.
