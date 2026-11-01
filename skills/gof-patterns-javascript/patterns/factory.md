# Factory

Function or method that creates objects in different ways: literals with
methods, class instances, or `Object.create(proto)` with a shared prototype.
The factory sets the whole object shape. It does not change after the factory
returns: no mix-ins or `setPrototypeOf`.

Refs: https://github.com/HowProgrammingWorks/Factory  
Example: [examples/factory.js](../examples/factory.js)

**Intent** — Centralize object birth so construction rules, defaults, and polymorphism stay in one place.

**Problem** — Call sites should not embed `new`, branching, or wiring every
time the object shape changes.

**Applicability** — **Use** for parametrized records, pooled or indexed instances, and objects sharing one prototype. **Avoid** a factory function when a single `class` is obvious and stable: calling `new` directly is enough.

**JS implementation** — Arrow factories, closures holding counters or config, small pure functions returning object literals. See `createUser` / connection factory in the example. Gotcha: the counter inside `createConnection` lives in module scope, so every importer of the module shares one sequence.

**Consequences** — Flexible and testable; overuse scatters unless factories are named and grouped by domain module.

**Related patterns** — **Factory Method** picks the type; **Abstract Factory** groups factories into families; **Prototype** for objects that are cheaper to clone than to rebuild.
