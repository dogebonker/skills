# Interface Segregation (ISP)

A caller should depend only on the methods it uses.

Refs: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf
Example: [examples/isp.rs](../examples/isp.rs)

**Principle** — Martin's 1996 paper names the cost of "fat" interfaces: every client depends on methods it never calls, and implementers carry methods they cannot support. In Rust the cure is small traits combined at the use site with bounds (`impl Print + Scan`) or supertraits (`trait Office: Print + Scan {}`). Bounds state exactly what a function needs, and impls exist only for the capabilities a type has.

**Violation signals** — A trait with many methods where most impls stub some with `unimplemented!()` or `Err("not supported")`, as `BasicPrinterV1` stubs `scan` and `fax`. Functions bounded on the fat trait but calling one method (`print_invoices_v1`).

**Fix** — One trait per capability: `Print` and `Scan`. `print_invoices` takes `&mut impl Print`, so `BasicPrinter` qualifies with no stubs; `copy_page` asks for `impl Print + Scan`, and only `MultiFunction` qualifies. A single-method dependency can also be a closure parameter (`impl FnMut(&str) -> Job`).

**When not to apply** — Splitting a trait whose methods are always used and implemented together (`Read`'s helpers, a codec's `encode`/`decode`). Many tiny traits cost names and bounds; split only where some implementer or caller genuinely needs a subset.

**Related** — **Adapter** (`gof-patterns-rust/patterns/adapter.md`) to fit a type to a narrow trait; **Facade** (`gof-patterns-rust/patterns/facade.md`) for the opposite, one wide entry point; **LSP** ([lsp.md](lsp.md)) for stub methods that break contracts; **DIP** ([dip.md](dip.md)) for who owns the trait; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
