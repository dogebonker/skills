# Abstract factory

Creates related objects belonging to one family without specifying their concrete classes, e.g., UI components for different platforms.

Refs: https://github.com/HowProgrammingWorks/AbstractFactory  
Example: [examples/abstract-factory.js](../examples/abstract-factory.js)

**Intent** — Expose one “family” API (e.g. `dataAccess.fs`) so products from that family stay consistent without naming each concrete class at call/instantiation places.

**Problem** — Switching stack (storage, UI kit, rendering method, etc.) should not scatter `new` and coupling logic across the app.

**Constraints** — Each family must implement the same conceptual roles; adding a new _role_ updates every family.

**Applicability** — **Use** when the app switches whole stacks by config or platform. **Avoid** an abstract factory when there is one family: a plain factory is enough.

**JS implementation** — Plain object or `Map` of families, each an object of factory functions (`dataAccess.memory`, `dataAccess.fs`); pick the family once by key and pass it down, or wire it from config with dynamic `import`/`require`. Gotcha: products of different families do not mix (`FileLineCursor` reads only a `FileStorage`), so take every product from the same family object.

**Consequences** — Swapping a family is one key; families drift unless a shared contract (`.d.ts`, tests) checks every role.

**Related patterns** — **Factory Method** creates each product inside a family; **Facade** often hides the family switch behind one API.
