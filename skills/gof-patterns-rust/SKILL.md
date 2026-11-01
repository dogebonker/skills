---
name: gof-patterns-rust
description: "GoF design patterns in Rust: all 22 creational, structural and behavioral patterns. Use when implementing, choosing, explaining or reviewing a design pattern in Rust code."
---

# GoF Patterns in Rust

- Keep patterns simple: the smallest version that removes the coupling or duplication you actually have.
- Use traits with generics (static dispatch) first, and reach for `Box<dyn Trait>` only when the type is chosen at runtime or the collection is heterogeneous.
- Use an `enum` with `match` for closed sets: it replaces State subclasses, Visitor double dispatch and many Factory products, and the compiler checks exhaustiveness.
- Use `Rc<RefCell<..>>` or `Weak` only when shared mutation is unavoidable (observer subscribers writing shared state); otherwise own children and pass ids or `&mut` down.
- Expect closures (`Fn`, `FnMut`, `FnOnce`) to be Strategy, Command and Observer callbacks, the `Iterator` trait (adaptors and `for` come free) to be Iterator, `OnceLock` or `LazyLock` in a `static` (never `static mut`) to be Singleton, `From`/`Into` and a newtype to be Adapter for foreign traits and types, builder methods taking `self` (with `Default`) or typestate to be Builder, `derive(Clone)` to be Prototype, a module with a private field to be Memento, and a plain function or `match` to make several other patterns unnecessary.
- Read the gotcha in an implementation section when it has one; most are ownership issues.

## How to use

Pick the pattern from the lists, then read its pattern file and its example before implementing, explaining, or reviewing it. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Each pattern has `patterns/<id>.md` and `examples/<id>.rs`, where `<id>` is the kebab-case name shown in the list (`chain-of-responsibility`). Read only the patterns the task needs.

## Creational patterns
- **Factory Method** (`factory-method`): Let one function decide which concrete type to build, so callers depend only on a trait.
- **Abstract Factory** (`abstract-factory`): Create families of related objects that must be used together.
- **Builder** (`builder`): Assemble a complex object step by step, with required parts enforced.
- **Prototype** (`prototype`): Create new objects by copying a configured instance.
- **Singleton** (`singleton`): Guarantee exactly one lazily built shared instance.

## Structural patterns
- **Adapter** (`adapter`): Make an incompatible type satisfy the interface your code expects.
- **Bridge** (`bridge`): Split an abstraction from its implementation so each varies on its own.
- **Composite** (`composite`): Treat single items and groups of items through the same interface.
- **Decorator** (`decorator`): Wrap an object to add behaviour while keeping the same interface.
- **Facade** (`facade`): Give a tangled subsystem one simple front door.
- **Flyweight** (`flyweight`): Share heavy immutable data between many small objects.
- **Proxy** (`proxy`): Stand in for an object to control access, defer work or cache.

## Behavioral patterns
- **Chain of Responsibility** (`chain-of-responsibility`): Pass a request along handlers until one deals with it.
- **Command** (`command`): Turn an action into a value that can be stored, queued or undone.
- **Iterator** (`iterator`): Walk a collection without exposing how it is stored.
- **Mediator** (`mediator`): Route communication between peers through one coordinator.
- **Memento** (`memento`): Capture and restore an object's state without breaking encapsulation.
- **Observer** (`observer`): Notify many subscribers when something happens.
- **State** (`state`): Change behaviour when internal state changes.
- **Strategy** (`strategy`): Swap an algorithm without changing the code that uses it.
- **Template Method** (`template-method`): Fix an algorithm's skeleton and let implementors fill the steps.
- **Visitor** (`visitor`): Add new operations over a fixed set of node types without changing them.
