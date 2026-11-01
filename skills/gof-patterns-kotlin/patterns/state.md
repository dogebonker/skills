# State

A sealed interface lists every state and an exhaustive `when` defines the transitions, so illegal states and missed cases fail at compile time.

Refs: https://refactoring.guru/design-patterns/state/java/example
Example: [examples/state.kt](../examples/state.kt)

**Intent** — Let an object change behaviour when its internal state changes.

**Problem** — An order behaves differently when created, shipped, delivered or cancelled, and `if` chains over a status field spread across the code.

**Applicability** — **Use** when behaviour depends on a state and there are many states and transitions. **Avoid** state classes when there are two or three states without complex per-state logic: an `enum` and a `when` is enough.

**Kotlin implementation** — `OrderState` is a sealed interface with `data object` and `data class` states. The extension `OrderState.on(event)` uses a nested exhaustive `when`, so adding a state or event breaks the build until handled. States carrying data, like `Shipped(tracking)`, use data classes. This is how UI state is modelled on Android: a sealed `UiState` (Loading, Content, Error) exposed from a ViewModel as `StateFlow`, rendered with `when`. Gotcha: an `else` branch in either `when` defeats exhaustiveness checks, so list states and events explicitly.

**Consequences** — Transitions are explicit and checked. Many states can make one large function, which you split by state.

**Related patterns** — **Strategy** lets the caller pick the behaviour, not a transition; **Observer** lets the UI react to state changes; **Command** for events that trigger transitions.
