# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction that the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf, https://developer.apple.com/videos/play/wwdc2015/408/
Example: [examples/dip.swift](../examples/dip.swift)

**Principle** — In Martin's paper the high-level policy stops depending on concrete devices once both sides depend on an abstraction. In Swift the abstraction is a protocol declared beside the consumer (a view model, a feature module), and the concrete client conforms through an extension. Inject it through `init`; use a generic parameter (static dispatch) or `any Protocol` when the type is chosen at runtime.

**Violation signals** — Stored properties initialised to concrete clients (`private let client = LiveWeatherClient()`), as `ForecastViewModelV1` has. Direct use of `URLSession.shared`, `UserDefaults.standard` or `FileManager.default` inside business logic. SwiftUI previews and tests that need the network.

**Fix** — Declare `ForecastProviding` beside `ForecastViewModel`, add `extension LiveWeatherClient: ForecastProviding {}`, and pass the provider in `init`. The app's composition root chooses `LiveWeatherClient`; previews pass `FixedForecast`. For one function, a closure parameter (`fetch: (String) -> Forecast`) is lighter than a protocol.

**When not to apply** — A protocol per type, each with one conformer, only to mock it. Value types and stable standard types (`Date`, `Array`) need no abstraction. Introduce the protocol when a second conformer or a module boundary appears.

**Related** — **Adapter** (`gof-patterns-swift/patterns/adapter.md`) for fitting an SDK to the protocol; **Factory Method** (`gof-patterns-swift/patterns/factory-method.md`) for choosing the detail at runtime; **Singleton** (`gof-patterns-swift/patterns/singleton.md`) for the `.shared` access this replaces; **ISP** ([isp.md](isp.md)) to keep the protocol small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
