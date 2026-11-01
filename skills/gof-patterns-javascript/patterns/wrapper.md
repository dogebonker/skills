# Wrapper

Function wrapper that delegates calls and adds behavior; a specialized case of Adapter.

Refs: https://github.com/HowProgrammingWorks/Wrapper  
Example: [examples/wrapper.js](../examples/wrapper.js)

**Intent** — Observe, throttle, or guard an existing callable without editing its body.

**Problem** — Cross-cutting concerns (logging, timeouts, metrics) should not duplicate inside every function.

**Applicability** — **Use** for HOF wrappers and interface-wide delegation. **Avoid** deep stacks of nested wrappers when the order matters: one middleware list in a clear order is enough.

**JS implementation** — `withLogging`, per-key wrapping of an object’s methods (`wrapInterface`), time-bounded execution like `Timeout`. Forward all arguments and return the result. Gotcha: an arrow wrapper has no `this` of its own, so a wrapped method that reads `this` needs a regular function calling `fn.apply(this, args)`.

**Consequences** — Readable composition; watch argument/`this` forwarding and async propagation.

**Related patterns** — **Decorator** stacks behavior on domain objects; **Proxy** for heavier object-level interception.
