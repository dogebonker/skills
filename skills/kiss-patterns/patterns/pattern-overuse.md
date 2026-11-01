# Pattern Overuse

Remove design patterns that add structure without solving a present problem: one-implementation interfaces, single-product factories and needless singletons.

Refs: https://refactoring.guru/smells/lazy-class
Example: [examples/pattern-overuse.ts](../examples/pattern-overuse.ts)

**Principle** — A pattern earns its classes when the problem it solves is in the code today. refactoring.guru's Lazy Class: a class that does too little to justify the cost of understanding it should be inlined. Mark Seemann's Reused Abstractions Principle (https://blog.ploeh.dk/2010/12/02/Interfacesarenotabstractions/) treats an interface with exactly one implementation as a smell. Singletons add hidden global state and make testing harder (https://en.wikipedia.org/wiki/Singleton_pattern).

**Violation signals** — `IPriceCalculator` with only `DefaultPriceCalculator`. A factory with one product (`PriceCalculatorFactory.create()`). `getInstance()` on a class with no shared resource. A Strategy chosen once from a constant. An Observer with one fixed listener. Interfaces that mirror one class method for method.

**Fix** — Inline toward the behaviour: replace the interface, class, factory and singleton with `priceWithTax(netCents)`. Pass dependencies as parameters, and use a module constant where one shared instance is needed. Reintroduce the pattern when a second variant or a real lifecycle need appears.

**When not to apply** — A single-implementation interface can be the seam to a slow or external system (payment gateway, clock) that tests replace with a fake, or a published plugin point. Language-native forms (functions for Strategy, modules for Singleton) are often the simple version, not overuse.

**Related** — **Singleton** (`gof-patterns-typescript/patterns/singleton.md`), **Factory Method** (`gof-patterns-typescript/patterns/factory-method.md`), **Abstract Factory** (`gof-patterns-typescript/patterns/abstract-factory.md`) and **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) for when each is warranted; [`speculative-generality`](speculative-generality.md); **DIP** (`solid-patterns-typescript/patterns/dip.md`) for interfaces with one implementation.
