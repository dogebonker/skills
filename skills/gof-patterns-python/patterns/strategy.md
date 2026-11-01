# Strategy

Interchangeable algorithms are passed in as functions behind one call signature.

Refs: https://refactoring.guru/design-patterns/strategy/python/example
Example: [examples/strategy.py](../examples/strategy.py)

**Intent** — Define a family of algorithms and let callers pick one at runtime.

**Problem** — A checkout needs different pricing rules (regular, sale, loyalty) without conditionals scattered across it.

**Applicability** — **Use** when behavior varies by a choice made at runtime. **Avoid** strategy classes with one method: a function is the strategy. Python functions are first-class, so `Callable[[float], float]` replaces the interface.

**Python implementation** — `Pricing = Callable[[float], float]`. `regular`, `black_friday` and `loyalty` are functions; `STRATEGIES` is a dict of callables for lookup by name (for example from config); `checkout(total, pricing=regular)` takes the function with a default. A lambda works for one-off rules (the last demo line). Use `functools.partial` to bind parameters, such as a rate. Use a class with state or a Protocol only when the strategy needs configuration or several methods. Gotcha: keep all strategies on the same signature.

**Consequences** — Open for extension, easy to test each function alone. Cost: callers need to know which strategy to choose.

**Related patterns** — **State** swaps behavior as state changes; **Command** wraps a request; **Template Method** varies steps via inheritance instead of composition; **Decorator** layers behavior.
