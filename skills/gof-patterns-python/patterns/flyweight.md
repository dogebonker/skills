# Flyweight

Share one immutable object for repeated intrinsic state, and keep per-use data outside it.

Refs: https://refactoring.guru/design-patterns/flyweight/python/example
Example: [examples/flyweight.py](../examples/flyweight.py)

**Intent** — Cut memory use when huge numbers of objects carry the same data.

**Problem** — A document with a million glyphs would repeat the same font and size information a million times.

**Applicability** — **Use** when profiling shows many near-identical objects dominate memory. **Avoid** a flyweight factory when a simple counted number is fine, or when `__slots__` on the class already reduces enough; also skip it for small data volumes.

**Python implementation** — `Style` is a `@dataclass(frozen=True)`, so it is immutable and hashable and safe to share. `get_style` is the flyweight factory: it builds the value, then returns the shared copy from a dict keyed by the value (`_STYLES.setdefault(style, style)`), so equal styles are one object however the call is written. `functools.lru_cache` is the tempting shortcut, but it keys on the call's spelling, so `get_style("Mono", 12)` and `get_style("Mono", 12, bold=False)` give two objects. Extrinsic state (`x`, `char`) lives in `Glyph`. Gotcha: never mutate shared objects, and note that unbounded caches keep objects alive; set `maxsize` if the key space is large. `sys.intern` does this for strings.

**Consequences** — Large memory savings. Cost: you separate state into intrinsic and extrinsic, which complicates code.

**Related patterns** — **Singleton** shares exactly one; **Composite** leaves are often flyweights; **Prototype** copies rather than shares; **State** and **Strategy** objects can be flyweights.
