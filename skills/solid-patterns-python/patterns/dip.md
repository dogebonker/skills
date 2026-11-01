# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf
Example: [examples/dip.py](../examples/dip.py)

**Principle** — Martin states two rules: high-level modules do not depend on low-level modules, and abstractions do not depend on details. The inversion is of ownership: the policy declares the interface and the detail conforms. In Python the abstraction is a `Protocol` or a `Callable` declared in the policy's module, and injection is an `__init__` or function argument; no framework is needed.

**Violation signals** — `SmsGateway()`, `boto3.client(...)` or `requests.get` called inside a domain class (`OrderServiceV1`). Domain modules importing infrastructure packages. Tests that need `unittest.mock.patch("pkg.module.Client")` to replace a dependency.

**Fix** — `OrderService` takes an `OrderNotifier` protocol in `__init__`. `SmsOrderNotifier` adapts the concrete `SmsGateway` to it and is built only in the composition root under `__main__`. The test double `RecordingNotifier` needs no base class and no patching.

**When not to apply** — A protocol with one implementation and no test double is ceremony; call the concrete class until a second implementation or a test needs the seam. Do not inject the standard library or pure helpers, and avoid default arguments that silently build the real detail, which hide the dependency again.

**Related** — **Adapter** (`gof-patterns-python/patterns/adapter.md`), as `SmsOrderNotifier` shows; **Strategy** (`gof-patterns-python/patterns/strategy.md`) for an injected callable; **Abstract Factory** (`gof-patterns-python/patterns/abstract-factory.md`) when the policy must create details; **Singleton** (`gof-patterns-python/patterns/singleton.md`), which injection replaces; **ISP** ([isp.md](isp.md)); **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
