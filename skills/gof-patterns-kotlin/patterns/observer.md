# Observer

Subscribers register lambdas with a subject and get called when it changes; `Flow` and `StateFlow` are the standard form on Android.

Refs: https://refactoring.guru/design-patterns/observer/java/example
Example: [examples/observer.kt](../examples/observer.kt)

**Intent** — Let many objects react to changes in one object without the subject knowing them.

**Problem** — A display and an alarm both depend on temperature, and the thermostat should not call them by name.

**Applicability** — **Use** when a change in one object must update others, and the set of listeners changes at runtime. **Avoid** a listener registry when one listener watches one property: `Delegates.observable` is enough. In Android, expose `StateFlow` from a ViewModel and collect it in the UI, or use `LiveData` in older code.

**Kotlin implementation** — `Thermostat.observe(listener: (Int) -> Unit)` stores the lambda and returns `() -> Unit` that removes it, so there is no separate remove method. `Delegates.observable` triggers notification on assignment. Iterate over `listeners.toList()` so listeners may unsubscribe during a callback. In real Android code, `MutableStateFlow` in a ViewModel with `collect` in a lifecycle-aware scope replaces this and handles threading and cancellation. Gotcha: unremoved listeners leak Activities, so always unsubscribe or use lifecycle-bound collection.

**Consequences** — Loose coupling between subject and listeners. Update order is unclear and leaks are easy.

**Related patterns** — **Mediator** for central coordination instead of broadcasting; **Command** for events as objects; **State** often triggers notifications when it changes.
