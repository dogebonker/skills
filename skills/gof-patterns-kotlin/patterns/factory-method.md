# Factory Method

An abstract class declares a creation function and each subclass (or a passed-in lambda) decides which concrete object it returns.

Refs: https://refactoring.guru/design-patterns/factory-method/java/example
Example: [examples/factory-method.kt](../examples/factory-method.kt)

**Intent** — Let a base class work with a product through its interface while subclasses choose the concrete product.

**Problem** — A service needs to send alerts but should not hard-code `EmailNotifier` or `PushNotifier`. New channels must not force edits in the service.

**Applicability** — **Use** when a base class has a fixed workflow but one step needs an object whose type varies by subclass. **Avoid** a subclass per product when the variation is only a value or a function: a `() -> Notifier` lambda, a function reference like `::PushNotifier`, or a top-level function with a `when` is enough.

**Kotlin implementation** — Declare the factory method `protected abstract fun createNotifier(): Notifier` in `AlertService`, and override it in `EmailAlertService` and `PushAlertService`. The base class calls it inside `alert`. `LambdaAlertService` in the example shows the function-typed version, which removes the subclass per product. On Android, `ViewModelProvider.Factory` and `Fragment` instantiation via `FragmentFactory` are the framework forms.

**Consequences** — Callers depend on an interface, and adding a product means adding one class. The cost is a subclass per product when a lambda would do.

**Related patterns** — **Abstract Factory** for several related products created together; **Template Method** usually calls a factory method as one of its steps; **Strategy** for swapping behaviour at runtime instead of creation.
