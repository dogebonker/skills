# Adapter

A small wrapper translates a foreign API into the interface your code already expects.

Refs: https://refactoring.guru/design-patterns/adapter/python/example
Example: [examples/adapter.py](../examples/adapter.py)

**Intent** — Let classes with incompatible interfaces work together without changing either.

**Problem** — A third-party client takes dollars as floats and uses different names, while your code calls `charge(cents, currency)`.

**Applicability** — **Use** when you cannot or should not change the wrapped code and want the rest of your program to see one interface. **Avoid** an Adapter class when a plain function converting arguments is enough, or when duck typing already fits (matching method names need no adapter).

**Python implementation** — Declare the target as a `Protocol` (`PaymentGateway`). `LegacyBankAdapter` holds the adaptee by composition, converts units (`cents / 100`) and normalises input (`currency.upper()`). Prefer composition over multiple inheritance. For a single method, pass a function or `functools.partial` instead. Gotcha: keep conversions (units, error types, naming) inside the adapter, so exceptions from the adaptee do not leak.

**Consequences** — Isolates third-party quirks to one place and eases replacement. Cost: one more layer to maintain.

**Related patterns** — **Facade** simplifies many classes instead of converting one; **Proxy** keeps the same interface; **Bridge** is designed up front, Adapter fixes things after the fact; **Decorator** adds behavior without changing the interface.
