---
name: gof-patterns-kotlin
description: "GoF design patterns in Kotlin for Android: all 22 creational, structural and behavioral patterns. Use when implementing, choosing, explaining or reviewing a design pattern in Kotlin or Android code."
---

# GoF Patterns in Kotlin

- Keep patterns simple: use the smallest form that solves the problem, and add a class hierarchy only when a function or data class cannot.
- Prefer the language feature that makes the pattern unnecessary: `object` for singleton (on Android a Hilt `@Singleton` or other DI scope, so tests can replace it), data class `copy()` for prototype and memento, default and named arguments for builder, function types and `fun interface` for strategy, listeners and one-method commands, extension functions for adapter, `Flow` and `StateFlow` collected in a lifecycle-aware scope for observer, `Sequence` with `sequence { yield() }` for iterator, sealed types with an exhaustive `when` for state, visitor and closed sets of commands, and class delegation with `by` for decorator and proxy.
- Recognise the Android form: ViewModel with StateFlow (observer, mediator), `RecyclerView.Adapter` (adapter), Intent and NavController (command, mediator), Fragment lifecycle (template method).
- Keep examples on the standard library; they are single `.kt` files with `fun main()`.

## How to use

Pick the pattern from the lists, then read its pattern file and its example before implementing, explaining, or reviewing it. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Read only the patterns the task needs. Each pattern has `patterns/<id>.md` and `examples/<id>.kt`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`).

## Creational patterns
- **Factory Method** (`factory-method`): let a base class run a workflow while subclasses (or a passed lambda) choose the object it creates.
- **Abstract Factory** (`abstract-factory`): create a matching family of objects, such as per-region tax and formatting, behind one interface.
- **Builder** (`builder`): build objects with many options or steps; try named and default arguments first, then a type-safe DSL.
- **Prototype** (`prototype`): make variants of a configured object; a data class `copy()` does it.
- **Singleton** (`singleton`): one instance per process; `object`, or a DI-scoped single instance on Android.

## Structural patterns
- **Adapter** (`adapter`): make a class you cannot change fit the interface your code expects, with an extension function or wrapper.
- **Bridge** (`bridge`): let two dimensions of variation, such as report type and output format, change independently.
- **Composite** (`composite`): treat a single item and a tree of items through one sealed type.
- **Decorator** (`decorator`): add behaviour by wrapping an object and delegating the rest with `by`.
- **Facade** (`facade`): give callers one simple function over several subsystem classes.
- **Flyweight** (`flyweight`): share many identical immutable objects through a cache to save memory.
- **Proxy** (`proxy`): stand in for an object to add caching, laziness or access control, with the same interface.

## Behavioral patterns
- **Chain of Responsibility** (`chain-of-responsibility`): pass a request through handlers until one answers, such as validation checks.
- **Command** (`command`): turn an action into an object when you need undo, queues or logs.
- **Iterator** (`iterator`): walk a custom structure in one or more orders with `Iterable` and `Sequence`.
- **Mediator** (`mediator`): route communication through one coordinator so participants do not know each other.
- **Memento** (`memento`): save and restore state with an immutable snapshot for undo or rollback.
- **Observer** (`observer`): notify many listeners when one object changes; `Flow` and `StateFlow` on Android.
- **State** (`state`): change behaviour with state, using a sealed type and an exhaustive `when`.
- **Strategy** (`strategy`): swap an algorithm at runtime by passing a function.
- **Template Method** (`template-method`): fix the order of steps in a base class and let subclasses fill in some steps.
- **Visitor** (`visitor`): add operations over a stable set of types with an exhaustive `when` over a sealed hierarchy.
