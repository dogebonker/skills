---
name: gof-patterns-javascript
description: "GoF design patterns in JavaScript: all 22 creational, structural and behavioral patterns, plus object pool and value-object boxing. Use when implementing, choosing, explaining or reviewing a design pattern in JavaScript code."
---

# GoF Patterns in JavaScript

Based on [metarhia/metaskills js-gof](https://github.com/metarhia/metaskills/tree/main/skills/js-gof) (MIT).

- Language features replace most pattern classes: functions in an object or `Map` for Strategy and dispatch, closures for Command, generators and `Symbol.iterator` for Iterator, `EventTarget` for portable Observer code (`EventEmitter` in Node), module scope for Singleton.
- Dispatch by object or `Map` lookup instead of a `switch`; guard keys that come from input with `Object.hasOwn` (or use a `Map`) so `toString` and `__proto__` never match.
- Keep internal state in `#private` fields and expose behavior, not storage.
- Prefer composition and functions over class hierarchies. Two examples extend built-in classes on purpose: `observer.js` extends `EventEmitter` to inherit its event API, and `proxy.js` extends `fs.ReadStream` because callers must still receive a real stream.
- Fail loudly: throw on an unknown key, an illegal transition or invalid input instead of returning `undefined`.
- Pass dependencies in (constructor, factory argument, context) instead of importing global state, and keep system code (IO, timers, transport) out of domain code.
- Examples are CommonJS (`'use strict'`, `require`, `module.exports`) and print a demo under `if (require.main === module)`. An ESM port swaps them for `import` and `export`.
- Keep patterns simple: use the smallest form that solves the problem, and skip the pattern when a plain function is enough.

## How to use

Pick the pattern from the lists, then read its pattern file (intent, problem, applicability, JS implementation, consequences, related patterns) and its example before implementing, explaining, or reviewing it. Each pattern has `patterns/<id>.md` and `examples/<id>.js`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`). Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Read only the patterns the task needs.

## Creational patterns

- **Abstract Factory** (`abstract-factory`): Switch a whole family of related objects (storage, UI kit) by one key.
- **Builder** (`builder`): Assemble a complex product from many optional, order-sensitive steps.
- **Factory Method** (`factory-method`): Pick the concrete class from input through a registry.
- **Prototype** (`prototype`): Clone a prepared instance instead of rebuilding it.
- **Singleton** (`singleton`): One shared instance; prefer module state, context, or DI.

## Structural patterns

- **Adapter** (`adapter`): Make a foreign interface match the one your code expects.
- **Bridge** (`bridge`): Let two hierarchies (features, implementations) vary independently.
- **Composite** (`composite`): Treat leaves and trees through one operation.
- **Decorator** (`decorator`): Layer optional behavior or metadata without subclassing.
- **Facade** (`facade`): One narrow API over a complex subsystem.
- **Flyweight** (`flyweight`): Share immutable intrinsic state among many small objects.
- **Proxy** (`proxy`): Control access to an object (stats, cache, policy) without built-in `Proxy`.

## Behavioral patterns

- **Chain of Responsibility** (`chain-of-responsibility`): Pass a request along reorderable handlers until one answers.
- **Command** (`command`): Turn an action into a value you can queue, log, or undo.
- **Iterator** (`iterator`): Traverse a collection lazily through `Symbol.iterator` and generators.
- **Mediator** (`mediator`): Route peer communication through one object so peers do not know each other.
- **Memento** (`memento`): Snapshot and restore state without exposing internals.
- **Observer** (`observer`): Notify many subscribers of a change with `EventEmitter` or `EventTarget`.
- **State** (`state`): Change behavior with the state, usually via a transition table.
- **Strategy** (`strategy`): Swap an algorithm by key through object/Map lookup of functions.
- **Template Method** (`template-method`): Fix an algorithm skeleton and let subclasses fill steps.
- **Visitor** (`visitor`): Add operations over a typed node tree without editing the nodes.

## Related non-GoF patterns

- **Factory** (`factory`): Centralize object creation: defaults, validation, and one final object shape.
- **Object Pool** (`object-pool`): Reuse expensive objects under bursty load.
- **Wrapper** (`wrapper`): Add cross-cutting behavior around a function or interface.
- **Boxing** (`boxing`): Give a primitive a validated domain type (value object).
- **Context** (`context`): Pass capabilities and request state between layers without globals.
