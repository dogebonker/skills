# Single Responsibility (SRP)

Keep together the code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://dave.cheney.net/2016/08/20/solid-go-design, https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.go](../examples/srp.go)

**Principle** — Martin defines a responsibility as a reason to change, and later as the group of people who ask for that change. Go has no classes, so the unit is the package and the function. Cheney's reading: a package name should say what it provides (`net/http`, `encoding/json`), and each package is one small tool.

**Violation signals** — Packages named `utils`, `common`, `helpers`, `server` or `models` that every other package imports. One function that parses input, applies a business rule and formats output, as `invoiceSummaryV1` does. A struct whose methods are edited in the same file by unrelated teams (pricing, layout, storage).

**Fix** — Split along reasons to change: `parseOrders` (input format), `withVAT` (finance rule) and `renderSummary` (layout), then compose them in `invoiceSummary`. In a real codebase move each into a package named for its purpose.

**When not to apply** — Splitting until every package holds one type and every function one line. Package count grows, names get vague, and callers chase three files to read one flow. Split when two reasons to change are real and present, not imagined.

**Related** — **Facade** (`gof-patterns-go/patterns/facade.md`) for a single entry point over the split parts; **Strategy** (`gof-patterns-go/patterns/strategy.md`) for passing the rule in as `func(int) int`; **ISP** ([isp.md](isp.md)) for the same split seen from the caller; **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`) for the overuse case.
