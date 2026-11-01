---
name: gof-patterns-python
description: "GoF design patterns in Python: all 22 creational, structural and behavioral patterns. Use when implementing, choosing, explaining or reviewing a design pattern in Python code."
---

# GoF Patterns in Python

- Keep patterns simple: the smallest structure that names the intent, with no speculative layers.
- Prefer the language feature that makes the pattern unnecessary: a function for Strategy and Command, a module-level instance for Singleton, a generator for Iterator, `singledispatch` for Visitor over an open set of types (`match` for a closed union), `dataclasses.replace` and `copy.deepcopy` for Prototype.
- Use `typing.Protocol` for interfaces so any object with the right methods qualifies; reach for `abc.ABC` only when you want instantiation of incomplete subclasses to fail (Template Method).
- Use first-class functions and `Callable` type aliases where a pattern has a single-method interface.
- Use a dict of callables or classes for dispatch and registries instead of `if/elif` chains.
- Use `@dataclass` (with `frozen=True` for values) for products, snapshots and nodes; use `field(default_factory=...)` for mutable defaults.
- Use context managers (`with`) for scoped setup and teardown (Template Method variants).
- Add type hints everywhere and `from __future__ import annotations` for self-referencing types; target Python 3.10 syntax.

## How to use

Pick the pattern from the lists, then read its pattern file and its example before implementing, explaining, or reviewing it. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Each pattern has `patterns/<id>.md` and `examples/<id>.py`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`). Read only the patterns the task needs.

## Creational patterns
- **Factory Method** (`factory-method`): let one place decide which concrete class to build; often a function or dict of classes is enough.
- **Abstract Factory** (`abstract-factory`): create a matching family of objects that must be used together.
- **Builder** (`builder`): assemble a complex object in steps and validate at the end; try dataclass defaults first.
- **Prototype** (`prototype`): make new objects by copying a configured one with `replace` or `deepcopy`.
- **Singleton** (`singleton`): share exactly one instance; use a module-level instance.

## Structural patterns
- **Adapter** (`adapter`): wrap an incompatible API so it fits the interface you use.
- **Bridge** (`bridge`): vary two independent dimensions by holding one behind a Protocol.
- **Composite** (`composite`): treat single items and trees of items through one interface.
- **Decorator** (`decorator`): layer extra behavior onto an object by wrapping it with the same interface.
- **Facade** (`facade`): offer one simple entry point over several subsystem calls.
- **Flyweight** (`flyweight`): share immutable repeated data to save memory.
- **Proxy** (`proxy`): stand in for an object to load it lazily, guard it or cache it.

## Behavioral patterns
- **Chain of Responsibility** (`chain-of-responsibility`): pass a request through ordered handlers until one answers.
- **Command** (`command`): turn an action into an object or callable you can queue, log or undo.
- **Iterator** (`iterator`): walk a collection without exposing its structure; write a generator.
- **Mediator** (`mediator`): route communication between peers through one coordinator.
- **Memento** (`memento`): save and restore an object's state with immutable snapshots.
- **Observer** (`observer`): notify many subscribers when something changes.
- **State** (`state`): change behavior as the object's state changes; start with an Enum and table.
- **Strategy** (`strategy`): swap interchangeable algorithms at runtime; pass a function.
- **Template Method** (`template-method`): fix an algorithm's skeleton and let subclasses fill in steps.
- **Visitor** (`visitor`): add operations over a set of node types, with `singledispatch` or `match`.
