# Interface Segregation (ISP)

A function should receive only the members it actually uses.

Refs: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf
Example: [examples/isp.js](../examples/isp.js)

**Principle** — Martin calls interfaces that serve several kinds of clients "fat" and shows that they couple those clients to each other. JavaScript has no interface declarations, so the fat interface shows up as a parameter: an `app`, `ctx`, `req` or service bag that a function reaches through. Its real dependency set is hidden in its body.

**Violation signals** — Chains like `app.services.customers.findEmail` and `app.config.brandName` inside domain code (`welcomeMessageV1`). Test fakes that rebuild nested objects to satisfy one call. Functions that take `options` and read one key.

**Fix** — Destructure exactly what is needed in the signature: `welcomeMessage(id, { findEmail, brandName })`. The caller passes `customers.findEmail` and a string; a test passes an arrow function. Duck typing means any function with the right behaviour fits. Destructure methods only when they do not use `this`, as with closure-based objects such as `createCustomerStore`.

**When not to apply** — Do not explode a cohesive object into ten parameters; passing the whole `customers` store is fine when the function uses most of it. A small, explicit context object at the request boundary is fine; the problem is a growing bag passed into domain code.

**Related** — **Context** (`gof-patterns-javascript/patterns/context.md`), which this keeps small; **Adapter** (`gof-patterns-javascript/patterns/adapter.md`) to expose a narrow view of a wide object; **Facade** (`gof-patterns-javascript/patterns/facade.md`); **SRP** ([srp.md](srp.md)); **DIP** ([dip.md](dip.md)), whose injected dependencies should be this narrow.
