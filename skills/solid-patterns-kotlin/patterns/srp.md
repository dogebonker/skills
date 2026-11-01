# Single Responsibility (SRP)

Group code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.kt](../examples/srp.kt)

**Principle** — A module should have one reason to change, and a reason is a person or group who asks for changes (Martin). It concerns cohesion of change, not "does one thing". Kotlin top-level functions need no class, so a pure responsibility can be a file of functions. On Android the guide's layers (UI, domain, data) are SRP at module scale: https://developer.android.com/topic/architecture/recommendations

**Violation signals** — One class mixes calculation, formatting and I/O (`InvoiceServiceV1.issue` computes VAT, builds text and stores it). A ViewModel or Activity that formats strings, calls Retrofit and writes Room rows. Classes named `*Manager` or `*Helper` that grow with every feature.

**Fix** — Split by actor: `invoiceTotalCents` (finance) and `renderInvoice` (layout) are top-level functions, `InvoiceArchive` (storage) is a small class, and `issueInvoice` composes them. On Android, move data access into a repository and multi-ViewModel logic into a use case.

**When not to apply** — Split only along an axis that actually changes; Martin notes that separating parts that always change together is needless complexity. A `UseCase` class with one `invoke` per trivial call, added before any ViewModel shares it, adds files without removing coupling; the Android guide recommends a domain layer only for big apps.

**Related** — **Facade** (`gof-patterns-kotlin/patterns/facade.md`) for the composing entry point; **Decorator** (`gof-patterns-kotlin/patterns/decorator.md`) to add logging or caching with `by` delegation; **ISP** ([isp.md](isp.md)); **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`).
