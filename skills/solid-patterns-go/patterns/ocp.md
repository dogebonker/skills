# Open/Closed (OCP)

Add new behavior by adding code, not by editing code that already works.

Refs: https://dave.cheney.net/2016/08/20/solid-go-design, https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html
Example: [examples/ocp.go](../examples/ocp.go)

**Principle** — Meyer coined it and Martin recast it: a module is open for extension and closed for modification. Martin's 1996 paper adds that no program is fully closed, so closure must be strategic, aimed at the changes most likely to happen. In Go, extension comes from small interfaces and function types; Cheney also notes that embedding adds methods to a type without changing the embedded type, but it is not inheritance: the inner methods never call back to the outer type.

**Violation signals** — A `switch format`, `switch kind` or `if provider == "..."` that gains a case with every feature. The same switch repeated in several files.

**Fix** — Depend on a one-method interface, as `export` depends on `Exporter`. Add a format as a new type (`CSVExporter`) or a function adapted by `ExporterFunc`, and register it in `main`. The loop stays untouched.

**When not to apply** — A closed, small set that rarely changes (three order states, two currencies) reads better as a `switch` in one place. An interface with a registry nobody extends is dead flexibility. Wait for the second or third variant.

**Related** — **Strategy** (`gof-patterns-go/patterns/strategy.md`) for swapping one algorithm; **Decorator** (`gof-patterns-go/patterns/decorator.md`) for extending by wrapping; **Adapter** (`gof-patterns-go/patterns/adapter.md`) for the `HandlerFunc` trick; **DIP** ([dip.md](dip.md)) for which side owns the interface; **YAGNI** (`kiss-patterns/patterns/yagni.md`) for unused extension points.
