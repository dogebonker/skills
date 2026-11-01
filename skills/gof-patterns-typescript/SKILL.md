---
name: gof-patterns-typescript
description: "GoF design patterns in TypeScript: all 22 creational, structural and behavioral patterns. Use when implementing, choosing, explaining or reviewing a design pattern in TypeScript code."
---

# GoF Patterns in TypeScript

- Keep patterns simple: the smallest structure that removes the problem, with no speculative extension points.
- Prefer the language feature that makes the pattern unnecessary: function types for Strategy and Command, discriminated unions for State and Visitor, ES modules for Singleton, `[Symbol.iterator]` generators for Iterator.
- Describe contracts with `interface` and rely on structural typing; implementers need no shared base class.
- Model state and node variants as discriminated unions and close every `switch` with a `never` check so new cases fail to compile.
- Use `#private` fields for runtime privacy; `private` only guards at compile time.
- Use `satisfies` to validate registries of strategies or factories while keeping literal keys.
- Write constructors with explicit fields instead of parameter properties so files also run under Node's type stripping.
- Use ES modules, `strict` mode, and `override` on overridden methods.

## How to use

Pick the pattern from the lists, then read its pattern file and its example before implementing, explaining, or reviewing it. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Each pattern has `patterns/<id>.md` and `examples/<id>.ts`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`). Read only the patterns the task needs.

## Creational patterns
- **Factory Method** (`factory-method`): let a subclass decide which concrete object a shared workflow creates.
- **Abstract Factory** (`abstract-factory`): create a matching family of objects (store + queue) that must be used together.
- **Builder** (`builder`): assemble a complex object step by step and validate it once at the end.
- **Prototype** (`prototype`): start new objects as deep copies of a configured one.
- **Singleton** (`singleton`): exactly one shared instance; in TypeScript, usually an exported module constant.

## Structural patterns
- **Adapter** (`adapter`): make an incompatible existing API fit the interface your code expects.
- **Bridge** (`bridge`): two independent axes of variation would otherwise multiply subclasses.
- **Composite** (`composite`): treat a single node and a group of nodes in a tree through one interface.
- **Decorator** (`decorator`): stack extra behaviour (logging, retry) around something with the same signature.
- **Facade** (`facade`): give callers one simple entry point to several subsystem calls.
- **Flyweight** (`flyweight`): share repeated immutable state across very many similar objects.
- **Proxy** (`proxy`): stand in front of a service to add lazy loading, caching or access control.

## Behavioral patterns
- **Chain of Responsibility** (`chain-of-responsibility`): pass a request along handlers until one deals with it.
- **Command** (`command`): turn an action into a value so it can be queued, logged or undone.
- **Iterator** (`iterator`): traverse a custom collection with `for...of` using `[Symbol.iterator]`.
- **Mediator** (`mediator`): route communication between components through one object instead of direct links.
- **Memento** (`memento`): snapshot and restore an object's state without exposing its internals.
- **Observer** (`observer`): notify many listeners when something changes.
- **State** (`state`): behaviour and allowed moves depend on a state that changes; model with a discriminated union.
- **Strategy** (`strategy`): swap interchangeable algorithms; model with function types.
- **Template Method** (`template-method`): fix an algorithm's step order in a base class and let subclasses fill in steps.
- **Visitor** (`visitor`): add operations over a stable set of node types; model with a union and exhaustive `switch`.
