# Decorator

An object wraps another with the same interface to add behavior, and wrappers can be stacked at runtime.

Refs: https://refactoring.guru/design-patterns/decorator/python/example
Example: [examples/decorator.py](../examples/decorator.py)

**Intent** — Attach responsibilities to an object dynamically without subclassing.

**Problem** — Combinations such as upper-case and bracketed output would need a subclass per combination.

**Applicability** — **Use** when you want to layer optional behavior on an object chosen at runtime. **Avoid** a decorator class when a function wrapper does the job: for callables, Python's `@decorator` syntax with `functools.wraps` is enough.

**Python implementation** — Be clear about the difference. The GoF Decorator wraps an *object* that satisfies a Protocol (`Upper(inner)`, `Bracketed(inner)`), and order matters, as the demo shows. Python's `@decorator` is syntax that rebinds a *function or class* name to the result of a callable; it implements the idea for functions, and `logged` shows it with `functools.wraps` preserving `__name__` and docstring. Neither requires the other. Gotcha: wrappers must forward the full interface, and `isinstance` checks see the wrapper, not the inner object.

**Consequences** — Flexible composition, single-purpose classes. Cost: many small objects and harder debugging of deep stacks.

**Related patterns** — **Proxy** has the same shape but manages access; **Adapter** changes the interface; **Composite** wraps many instead of one; **Chain of Responsibility** can stop the flow.
