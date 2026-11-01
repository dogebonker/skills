# Factory Method

An abstract base class declares a protected `create…()` method that subclasses override to return the concrete object the shared workflow uses.

Refs: https://refactoring.guru/design-patterns/factory-method/typescript/example
Example: [examples/factory-method.ts](../examples/factory-method.ts)

**Intent** — Let a base class run a workflow while subclasses choose which concrete object it works with.

**Problem** — A workflow needs an object whose exact class varies, and hard-coding `new EmailNotifier()` inside it would block every other variant.

**Applicability** — **Use** when a workflow is fixed but one collaborator varies by subclass, or a framework must let users plug in their own product type. **Avoid** a Creator subclass hierarchy when a plain function returning an interface value does the job (`const make = (kind: Kind): Notifier => ...`), or a union-keyed record of constructors does.

**TypeScript implementation** — Declare the product as an `interface` (`Notifier`) and the creator as an `abstract class` (`Alert`) with `protected abstract createNotifier()`. The template method `raise` calls it. Structural typing means products need no shared base class, only matching members. Gotcha: calling the factory method from a constructor runs before subclass fields are initialised.

**Consequences** — Callers depend only on the interface, and new variants need a new subclass, not edits. The cost is a parallel class hierarchy for what is often a one-line function.

**Related patterns** — **Abstract Factory** covers several related products that must vary together; **Template Method** usually contains the creator.
