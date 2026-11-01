# Open/Closed (OCP)

Add new behaviour by adding code, not by editing code that already works.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html
Example: [examples/ocp.py](../examples/ocp.py)

**Principle** — A module is open for extension and closed for modification (Meyer, restated by Martin). Martin's 1996 paper adds that no program is fully closed, so closure is strategic: choose the changes you expect. In Python the extension point is a mapping of callables, a `functools.singledispatch` function, a plugin registry or an entry point, more often than a subclass.

**Violation signals** — An `if/elif` chain or `match` on a string kind (`fee_cents_v1` on `p.method`) edited for every variant and copied across modules. `isinstance` ladders over types you do not own. Flags such as `mode="legacy"` that pick branches deep inside a function.

**Fix** — Make the variants data: `DEFAULT_FEE_RULES` is a read-only `MappingProxyType` of `FeeRule` callables, and `fee_cents` looks the rule up and raises on an unknown key. A caller extends it with `{**DEFAULT_FEE_RULES, "voucher": ...}`; `fee_cents` is not edited. For dispatch on argument type, `singledispatch` lets other modules `register` new types.

**When not to apply** — A short `match` over a closed set you own reads better than a registry, and a type checker can check exhaustiveness on a `Literal` or `Enum`. Registries that only one module ever fills are speculative generality, and they hide control flow from readers.

**Related** — **Strategy** (`gof-patterns-python/patterns/strategy.md`) is the mechanism; **Visitor** (`gof-patterns-python/patterns/visitor.md`) for `singledispatch`; **Decorator** (`gof-patterns-python/patterns/decorator.md`) to extend by wrapping; **DIP** ([dip.md](dip.md)); **Data over code** (`kiss-patterns/patterns/data-over-code.md`); **YAGNI** (`kiss-patterns/patterns/yagni.md`).
