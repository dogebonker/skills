# Open/Closed (OCP)

Add new behaviour by adding code, not by editing code that already works.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html
Example: [examples/ocp.kt](../examples/ocp.kt)

**Principle** — A module is open for extension and closed for modification (Meyer, restated by Martin). Martin's 1996 paper adds that no program is fully closed, so closure is strategic: choose the changes you expect. Kotlin offers two opposite tools: a map of functions or an interface for an open set, and a `sealed` type for a closed set whose exhaustive `when` makes the compiler list every site to edit (https://kotlinlang.org/docs/sealed-classes.html).

**Violation signals** — A `when` on a string or enum (`feeCentsV1` on `p.method`) edited for every new variant and repeated across classes, with an `else -> throw`. A new payment provider touches the ViewModel, the repository and the mapper.

**Fix** — Make the variants data: `defaultFeeRules` is a `Map<String, FeeRule>` where `FeeRule` is a function `typealias`, and `feeCents` looks the rule up and throws on an unknown key. A caller extends it with `defaultFeeRules + ("voucher" to ...)`.

**When not to apply** — If the set is closed and yours, a sealed interface with an exhaustive `when` and no `else` is safer than a map: adding a case breaks the build at every site instead of failing at runtime. Map registries that one module ever fills are speculative generality.

**Related** — **Strategy** (`gof-patterns-kotlin/patterns/strategy.md`) is the mechanism; **Visitor** (`gof-patterns-kotlin/patterns/visitor.md`) for the sealed `when` alternative; **Decorator** (`gof-patterns-kotlin/patterns/decorator.md`); **DIP** ([dip.md](dip.md)); **Data over code** (`kiss-patterns/patterns/data-over-code.md`); **YAGNI** (`kiss-patterns/patterns/yagni.md`).
