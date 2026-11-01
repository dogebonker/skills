# Open/Closed (OCP)

Add new behaviour by adding code, not by editing code that already works.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html
Example: [examples/ocp.js](../examples/ocp.js)

**Principle** — A module is open for extension and closed for modification (Meyer, restated by Martin). Martin's 1996 paper adds that no program is fully closed, so closure is strategic: choose the changes you expect. In JavaScript the extension point is a function, an object or `Map` of functions, or a plugin array, rarely a subclass.

**Violation signals** — A `switch` or `if/else` on a string kind (`feeCentsV1` on `method`) that is edited for every new variant, often copied across files. Boolean options that pick branches deep inside a function. A new provider means edits in five places.

**Fix** — Make the variants data: `defaultFeeRules` is a frozen object of functions, and `feeCents` looks the rule up with `Object.hasOwn` so inherited keys such as `toString` never match. A caller extends it by spreading a new entry (`voucher`) and `feeCents` is not edited. Throw on an unknown key instead of returning `undefined`.

**When not to apply** — A short, stable `switch` over cases you own is easier to read than a registry. Plugin hooks that no second caller uses are speculative generality, and a lookup table hides control flow from "go to definition".

**Related** — **Strategy** (`gof-patterns-javascript/patterns/strategy.md`) is the mechanism; **Decorator** (`gof-patterns-javascript/patterns/decorator.md`) to extend by wrapping; **Chain of Responsibility** (`gof-patterns-javascript/patterns/chain-of-responsibility.md`) for plugin arrays; **DIP** ([dip.md](dip.md)); **Data over code** (`kiss-patterns/patterns/data-over-code.md`); **YAGNI** (`kiss-patterns/patterns/yagni.md`).
