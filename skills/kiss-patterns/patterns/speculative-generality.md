# Speculative Generality

Remove hooks, parameters, base classes and indirection added for needs that never came.

Refs: https://refactoring.guru/smells/speculative-generality
Example: [examples/speculative-generality.py](../examples/speculative-generality.py)

**Principle** — refactoring.guru names unused classes, methods, fields and parameters, built "just in case", as a dispensable smell. They cost reading time and constrain every change while delivering nothing. Where YAGNI is about features, this smell is about structure.

**Violation signals** — An abstract base class with one subclass (`BaseNotifier` and `EmailNotifier`). Hook methods no subclass overrides (`before_send`). Parameters every caller leaves at the default (`retries=0`) or never passes (`transform`). Generic type parameters always bound to one type. Delegating classes that forward every call.

**Fix** — Apply the treatments in turn: Collapse Hierarchy for an abstract class with one child, Inline Class for needless delegation, Inline Method, Remove Parameter, and delete unused fields. In the example the class pair becomes `send_email(outbox, to, message)`. Search callers and tests before each removal.

**When not to apply** — Library and framework code may expose hooks that only outside users call; check the public API before deleting. Tests may use an element to reach internal state. A seam needed for a test double counts as a real use.

**Related** — **Template Method** (`gof-patterns-typescript/patterns/template-method.md`) for hook methods nobody overrides; **Factory Method** (`gof-patterns-typescript/patterns/factory-method.md`) with one product; [`pattern-overuse`](pattern-overuse.md); [`yagni`](yagni.md); [`wrong-abstraction`](../../dry-patterns/patterns/wrong-abstraction.md); **ISP** (`solid-patterns-typescript/patterns/isp.md`); **DIP** (`solid-patterns-typescript/patterns/dip.md`).
