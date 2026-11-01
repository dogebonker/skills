---
name: gof-patterns-go
description: "GoF design patterns in Go: all 22 creational, structural and behavioral patterns. Use when implementing, choosing, explaining or reviewing a design pattern in Go code."
---

# GoF Patterns in Go

- Keep patterns simple: write the smallest code that solves the stated problem, and skip the pattern when plain Go already does.
- Prefer the language feature that removes the pattern: function types for Strategy, Command and Chain of Responsibility, `iter.Seq` for Iterator, `for range` over slices and maps, struct literals for Prototype of value types, enums and `switch` for State and Visitor, functional options (`...Option`) for Builder, `sync.OnceValue` for Singleton (a package-level var or dependency injection is simpler and easier to test), and an interface that a function calls for Template Method steps.
- Define small interfaces where they are consumed, not where they are implemented; one or two methods is typical.
- Return concrete types from constructors unless callers truly need to hide the type (Factory Method returns an interface, `NewX` otherwise returns `*X`).
- Use struct embedding for reuse and default behavior, not as inheritance; it promotes methods but does not dispatch back to the outer type.
- Reach for channels only where they fit, mainly Observer fan-out, and pass `context.Context` where cancellation matters.
- Treat errors as values: return `error` from factories, handlers and transitions, and wrap with `%w`.
- Guard shared state in proxies, caches and subjects with a mutex, and run the race detector when goroutines are involved.

## How to use

Pick the pattern from the lists, then read its pattern file and its example before implementing, explaining, or reviewing it. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Each pattern has `patterns/<id>.md` and `examples/<id>.go`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`). Read only the patterns the task needs.

## Creational patterns
- **Factory Method** (`factory-method`): reach for it when you need to create a value without callers naming its concrete type.
- **Abstract Factory** (`abstract-factory`): reach for it when you must create families of related objects that must be used together.
- **Builder** (`builder`): reach for it when an object has many optional settings or needs stepwise construction.
- **Prototype** (`prototype`): reach for it when new values should start as copies of an existing configured value.
- **Singleton** (`singleton`): reach for it when exactly one shared instance must exist and be created lazily and safely.

## Structural patterns
- **Adapter** (`adapter`): reach for it when you must make an existing type fit an interface it does not satisfy.
- **Bridge** (`bridge`): reach for it when two independent dimensions of variation would otherwise multiply into many types.
- **Composite** (`composite`): reach for it when individual items and groups of items must be treated through one interface.
- **Decorator** (`decorator`): reach for it when you want to add behavior around an existing object without changing its type.
- **Facade** (`facade`): reach for it when callers need one simple entry point over several subsystems.
- **Flyweight** (`flyweight`): reach for it when many objects would otherwise duplicate the same large immutable data.
- **Proxy** (`proxy`): reach for it when you need a stand-in that controls access to another object with the same interface.

## Behavioral patterns
- **Chain of Responsibility** (`chain-of-responsibility`): reach for it when a request should pass through a sequence of handlers until one deals with it.
- **Command** (`command`): reach for it when an action must be stored, queued, logged or undone.
- **Iterator** (`iterator`): reach for it when callers need to traverse a collection without knowing its structure.
- **Mediator** (`mediator`): reach for it when many components talk to each other and direct links make the web hard to change.
- **Memento** (`memento`): reach for it when you must capture and later restore an object's state without exposing its internals.
- **Observer** (`observer`): reach for it when several parties must react to events from one source without it knowing them.
- **State** (`state`): reach for it when an object's behavior depends on a mode, and the allowed changes between modes need rules.
- **Strategy** (`strategy`): reach for it when an algorithm must be chosen or swapped at runtime.
- **Template Method** (`template-method`): reach for it when an algorithm has a fixed skeleton with steps that vary.
- **Visitor** (`visitor`): reach for it when you need new operations over a fixed set of types without editing each type.
