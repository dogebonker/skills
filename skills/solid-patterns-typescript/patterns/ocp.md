# Open/Closed (OCP)

Add new behaviour by adding code, not by editing code that already works.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html
Example: [examples/ocp.ts](../examples/ocp.ts)

**Principle** — A module is open for extension and closed for modification (Meyer, restated by Martin). Martin's 1996 paper adds that no program is fully closed, so closure is strategic: pick the changes you expect. In TypeScript the extension point is usually a function type or a table of functions, not a subclass.

**Violation signals** — A `switch` or `if/else` on a string kind (`feeCentsV1` on `p.method`) that is edited for every new variant, often repeated in several files. Feature flags threaded through one function. Shotgun edits when a new provider is added.

**Fix** — Make the variant data: `FeeRules` is a `Record<string, FeeRule>` checked with `satisfies`, and `feeCents` looks the rule up with `Object.hasOwn`. A caller extends it by spreading a new entry (`voucher`) without touching `feeCents`.

**When not to apply** — If the set of cases is closed and owned by you, a discriminated union with an exhaustive `switch` and a `never` check is clearer and makes the compiler find every site when a case is added. Extension points nobody extends are speculative generality.

**Related** — **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) is the usual mechanism; **Visitor** (`gof-patterns-typescript/patterns/visitor.md`) for the closed-union alternative; **Decorator** (`gof-patterns-typescript/patterns/decorator.md`) to extend by wrapping; **DIP** ([dip.md](dip.md)) points the dependency at the extension point; **Data over code** (`kiss-patterns/patterns/data-over-code.md`); **YAGNI** (`kiss-patterns/patterns/yagni.md`).
