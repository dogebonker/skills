---
name: gof-patterns-swift
description: "GoF design patterns in Swift: all 22 creational, structural and behavioral patterns. Use when implementing, choosing, explaining or reviewing a design pattern in Swift code."
---

# GoF Patterns in Swift

- Keep patterns simple: add one only when a concrete variation or coupling problem exists, and stop at the smallest form that solves it.
- Prefer the language feature that makes the pattern unnecessary: closures for strategy and command, enums with `switch` for state and visitor, default arguments for builder, value semantics for prototype, `Sequence` and `IteratorProtocol` for iterator, `AsyncStream`, Combine or Observation for observer, generics for decorator stacks, and `static let shared` for singleton, though an `init` parameter is usually better because tests can pass a fresh instance.
- Use protocols and protocol extensions instead of class inheritance; put shared algorithm steps (template method, factory method callers) in extensions.
- Use `struct` and `enum` by default; reach for `final class` only for identity, shared mutation, or framework requirements.
- Model alternatives as enums with associated values and exhaustive `switch`, so adding a case becomes a compile error everywhere it matters.
- Use closures for single-method behavior and take them as `@escaping` parameters when you store them; mark them `@Sendable` when they cross concurrency domains.
- Write for Swift 6 language mode: shared mutable state belongs in an `actor` or `@MainActor` type, and shared data must be `Sendable`.
- Use `some` for static dispatch and `any` for runtime-chosen values.
- SwiftUI and UIKit have counterparts for several patterns (`ViewBuilder`, `ViewModifier`, `UndoManager`, delegates); the pattern files name them.

## How to use

Pick the pattern from the lists, then read its pattern file and its example before implementing, explaining, or reviewing it. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Read only the patterns the task needs. Each pattern has `patterns/<id>.md` and `examples/<id>.swift`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`).

## Creational patterns
- **Factory Method** (`factory-method`): let a conforming type decide which concrete product a shared routine works with.
- **Abstract Factory** (`abstract-factory`): create a matching family of related objects without naming concrete types.
- **Builder** (`builder`): assemble an object with many optional parts step by step into an immutable result.
- **Prototype** (`prototype`): make new objects by copying a configured one.
- **Singleton** (`singleton`): keep exactly one shared instance with safe access.

## Structural patterns
- **Adapter** (`adapter`): make an existing API fit the protocol your code expects.
- **Bridge** (`bridge`): vary an abstraction and its implementation independently by composition.
- **Composite** (`composite`): treat single items and groups in a tree the same way.
- **Decorator** (`decorator`): add behavior by wrapping an object that has the same interface.
- **Facade** (`facade`): give a complex set of subsystems one simple entry point.
- **Flyweight** (`flyweight`): share identical immutable state across many small objects to save memory.
- **Proxy** (`proxy`): put a stand-in in front of an object to control access, cache, or load lazily.

## Behavioral patterns
- **Chain of Responsibility** (`chain-of-responsibility`): pass a request along handlers until one deals with it.
- **Command** (`command`): package an action, with undo, as a value that can be stored and replayed.
- **Iterator** (`iterator`): walk a custom collection without exposing how it is stored.
- **Mediator** (`mediator`): route communication between peers through one coordinator.
- **Memento** (`memento`): save and restore an object's state without exposing its internals.
- **Observer** (`observer`): notify many subscribers when a source changes.
- **State** (`state`): change behavior as internal state changes, with transitions in one place.
- **Strategy** (`strategy`): swap interchangeable algorithms at runtime.
- **Template Method** (`template-method`): fix an algorithm's order and let implementers fill in steps.
- **Visitor** (`visitor`): add new operations over a stable set of node types.
