# Builder

Functional options: variadic `Option` funcs that mutate a struct inside the constructor.

Refs: https://refactoring.guru/design-patterns/builder/go/example
Example: [examples/builder.go](../examples/builder.go)

**Intent** — Construct a complex object step by step, letting callers set only the parts they care about.

**Problem** — A constructor with eight parameters, most of them optional, forces callers to pass zero values and breaks whenever a field is added.

**Applicability** — **Use** when a type has several optional parameters with sensible defaults, and you want a stable constructor signature. **Avoid** functional options when there are one or two parameters or every field is required: plain arguments or a struct literal is enough.

**Go implementation** — Define `type Option func(*Server)`, write `WithTimeout`, `WithTLS` and similar option constructors, and have `NewServer(addr, opts...)` set defaults, apply options in order, then validate and return `(*Server, error)`. Required values stay positional arguments. Validation belongs after options run, as in the `maxConn` check. A chained `Builder` struct with `Build()` is only worth it when construction is genuinely multi-phase or needs to produce different representations.

**Consequences** — The API grows without breaking callers and reads clearly. The cost is one function per option and no compile-time check that required options were supplied beyond positional arguments.

**Related patterns** — **Abstract Factory** for a result that is a family selected at once; **Prototype** for starting from a configured copy instead.
