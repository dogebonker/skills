# Template Method

A trait whose provided method calls required methods and optional hooks with defaults.

Refs: https://refactoring.guru/design-patterns/template-method/rust/example
Example: [examples/template-method.rs](../examples/template-method.rs)

**Intent** — Define the skeleton of an algorithm once and let implementors supply the varying steps.

**Problem** — Every report job fetches rows, formats them and prints a header, but each report differs in the details.

**Applicability** — **Use** when several types share a workflow and differ in some steps. **Avoid** a template trait with one impl per variant when a function can take the varying steps as closures or generic arguments: that function is enough.

**Rust implementation** — `trait ReportJob` declares required `fetch` and `format_row`, a default `header` hook, and a default `run` that is the template. Implementors override only what differs. Rust cannot forbid overriding `run`, so state in a doc comment that it is not meant to be overridden, or put the template in a free function `fn run(job: &impl ReportJob)`, or in an extension trait with a blanket impl (`trait RunReport: ReportJob { fn run(&self) -> String {..} } impl<T: ReportJob> RunReport for T {}`), which no type can override. The gotcha: default methods cannot access fields, only the trait's methods, so required methods carry the data.

**Consequences** — Reuse of a workflow with controlled variation. The cost is coupling through the trait, and traits are less flexible than closures.

**Related patterns** — **Strategy** swaps whole algorithms rather than steps; **Factory Method** is often a step in a template; **Decorator** extends behaviour from outside.
