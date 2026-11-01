# Single Responsibility (SRP)

Group code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.ts](../examples/srp.ts)

**Principle** — A module should have one reason to change, and a reason is a person or group who asks for changes (Martin). It is about cohesion of change, not "does one thing". In TypeScript the module is usually a file or a function, not a class.

**Violation signals** — One class mixes calculation, formatting and I/O (`InvoiceServiceV1.issue` computes VAT, builds text and stores it). Imports from both `node:fs` or `fetch` and pure domain types in one file. Names with `And`, `Manager`, `Util`. Unrelated tests break together.

**Fix** — Extract each concern as a plain exported function or a small class: `invoiceTotalCents` (finance), `renderInvoice` (layout), `InvoiceArchive` (storage). A thin `issueInvoice` composes them. Pure functions need no class at all.

**When not to apply** — Split only along an axis that actually changes; Martin notes that separating parts that always change together is needless complexity. A one-method class per verb, or a file per three-line function, scatters one idea across many files.

**Related** — **Facade** (`gof-patterns-typescript/patterns/facade.md`) for the composing entry point; **Decorator** (`gof-patterns-typescript/patterns/decorator.md`) to add logging or caching without growing the class; **ISP** ([isp.md](isp.md)) splits interfaces by client the way SRP splits modules by actor; **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`) for the overuse case.
