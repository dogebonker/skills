# Single Responsibility (SRP)

Group code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.py](../examples/srp.py)

**Principle** — A module should have one reason to change, and a reason is a person or group who asks for changes (Martin). It concerns cohesion of change, not "does one thing". In Python the module really is the unit: a `.py` file of functions is a first-class home for one responsibility, and a class is needed only for state.

**Violation signals** — One class mixes calculation, formatting and I/O (`InvoiceServiceV1.issue` computes VAT, builds text and stores it). Imports of `sqlite3`, `requests` or `open()` next to business rules. Classes named `*Manager` or `utils.py` files that every change touches.

**Fix** — Split by actor: `invoice_total_cents` (finance), `render_invoice` (layout) and `InvoiceArchive` (storage). `issue_invoice` composes them in three lines. Keep the pure parts as module-level functions; only the stateful part is a class.

**When not to apply** — Split only along an axis that actually changes; Martin notes that separating parts that always change together is needless complexity. A class per verb with one method and an `__init__` is a function in disguise, and a package per tiny module costs more imports than it saves.

**Related** — **Facade** (`gof-patterns-python/patterns/facade.md`) for the composing entry point; **Decorator** (`gof-patterns-python/patterns/decorator.md`) to add logging or caching as a function decorator instead of more code in the class; **ISP** ([isp.md](isp.md)); **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`) for the overuse case.
