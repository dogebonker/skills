# Single Responsibility (SRP)

Group code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.js](../examples/srp.js)

**Principle** — A module should have one reason to change, and a reason is a person or group who asks for changes (Martin). It concerns cohesion of change, not "does one thing". In JavaScript the natural unit is a module file or a function; classes are optional.

**Violation signals** — One class or file mixes calculation, formatting and I/O (`InvoiceServiceV1.issue` computes VAT, builds text and stores it). A file that `require`s both `fs` or `http` and holds business rules. Names with `And`, `Manager`, `helpers`. One change request touches unrelated lines of the same function.

**Fix** — Export each concern separately: `invoiceTotalCents` (finance), `renderInvoice` (layout), `createInvoiceArchive` (storage, a closure over a `Map`). `issueInvoice` composes them and stays a few lines long. Pure functions are the cheapest unit to test.

**When not to apply** — Split only along an axis that actually changes; Martin notes that separating parts that always change together is needless complexity. A module per three-line function, or classes holding one method, scatter one idea across many files.

**Related** — **Facade** (`gof-patterns-javascript/patterns/facade.md`) for the composing entry point; **Wrapper** (`gof-patterns-javascript/patterns/wrapper.md`) to add logging or timing without growing the function; **ISP** ([isp.md](isp.md)) splits what a function receives the way SRP splits modules; **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`) for the overuse case.
