# Template Method

A protocol extension supplies the fixed algorithm and calls requirements that conforming types implement.

Refs: https://refactoring.guru/design-patterns/template-method/swift/example
Example: [examples/template-method.swift](../examples/template-method.swift)

**Intent** — Define the skeleton of an algorithm in one place and let subtypes fill in specific steps.

**Problem** — Several report generators follow the same fetch, format, finish sequence with different details.

**Applicability** — **Use** when the order of steps is fixed and only some steps vary. **Avoid** a base class with overridable steps when only a few steps vary: a function that takes closures, or a protocol extension, is enough.

**Swift implementation** — Declare the steps as protocol requirements (`fetchRows`, `format`) and implement `generate()` in an extension, as `ReportGenerator` does. Give optional steps default implementations (`wantsFooter`). Because `generate()` is not a requirement it is statically dispatched: a conformer that declares its own `generate()` silently shadows it when called on the concrete type, while generic and `any` callers still get the template. Do not redeclare it. With classes, mark the template `final` and steps overridable.

**Consequences** — Reuse of the algorithm and consistent flow. Many hooks make it rigid; deep hierarchies hurt.

**Related patterns** — **Strategy** uses composition instead; **Factory Method** is often a step; **Decorator** alters behavior from outside.
