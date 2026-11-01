# Interface Segregation (ISP)

A caller should depend only on the methods it uses.

Refs: https://dave.cheney.net/2016/08/20/solid-go-design, https://go.dev/wiki/CodeReviewComments#interfaces
Example: [examples/isp.go](../examples/isp.go)

**Principle** — Martin's 1996 paper warns against "fat" interfaces whose clients each use a different slice of them. Go makes the fix cheap: interfaces are satisfied implicitly, so the consumer declares the small interface it needs, next to itself, and existing types already satisfy it. Cheney's example narrows `Save(f *os.File)` to `Save(w io.Writer)`. The Go code review guide says interfaces belong in the package that uses them, and producers should return concrete types.

**Violation signals** — An interface of five or more methods declared beside its only implementation (`OrderRepository` next to `memRepo`). Functions that take it but call one method, as `monthlyRevenueV1` does. Test fakes full of methods that `panic("not implemented")`. Parameters typed `*os.File` or `*sql.DB` where only reading or writing is needed.

**Fix** — Declare `monthLister` with the one method, beside `monthlyRevenue`. `*memRepo` satisfies it with no change, and a test passes `fixedOrders`, a slice type with one method.

**When not to apply** — Splitting a cohesive interface used whole by every caller (`sort.Interface` needs all three methods). Defining a one-method interface for a single concrete caller and a single implementation, only "for testing": pass the concrete type or a function instead.

**Related** — **Adapter** (`gof-patterns-go/patterns/adapter.md`) to fit a type to a narrow interface; **Facade** (`gof-patterns-go/patterns/facade.md`) for the opposite direction, one wide entry point; **LSP** ([lsp.md](lsp.md)) and **DIP** ([dip.md](dip.md)) for who owns the interface; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`) for single-implementation interfaces.
