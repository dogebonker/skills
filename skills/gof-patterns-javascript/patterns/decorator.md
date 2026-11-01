# Decorator

Wraps an object with the same interface to add behavior; layers stack in any order.

Refs: https://github.com/HowProgrammingWorks/Decorator  
Example: [examples/decorator.js](../examples/decorator.js)

**Intent** — Layer optional behaviors (validation, logging) or metadata around a core object in a composable order.

**Problem** — Subclass explosion for every combination of add-ons.

**Applicability** — **Use** when optional checks or behaviors combine in different orders. **Avoid** TC39 `@decorator` syntax when the project does not already use it: plain wrapper objects or functions are enough.

**JS implementation** — Validator objects wrapping a `next` validator (same `validate` contract at every layer), `Symbol` keys for metadata set in the constructor, `WeakMap` for metadata kept outside the object. See the example. Gotcha: the innermost layer needs a terminal `next` (`PASS`); `MinLengthValidator` has no default, so building it without `next` throws on the first `validate`.

**Consequences** — Flexible order; document pipeline order; watch for double-wrapped side effects.

**Related patterns** — **Wrapper** for the same idea applied to functions; **Chain of Responsibility** lets each link stop processing.
