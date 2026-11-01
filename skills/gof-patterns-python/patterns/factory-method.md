# Factory Method

A creator class (or plain function) decides which concrete object to build, so calling code depends only on a Protocol.

Refs: https://refactoring.guru/design-patterns/factory-method/python/example
Example: [examples/factory-method.py](../examples/factory-method.py)

**Intent** — Move object creation into one overridable method or function so the rest of the code never names concrete classes.

**Problem** — A workflow such as sending an alert is identical for email and SMS except for which notifier it constructs. Hard-coding `EmailNotifier()` blocks new channels.

**Applicability** — **Use** when a shared workflow needs a product whose type varies by subclass or configuration. **Avoid** a Creator subclass hierarchy when a function or a `dict[str, type]` lookup does the job: classes are first-class values in Python, so `NOTIFIERS[kind]()` is often the whole pattern.

**Python implementation** — Define the product as a `typing.Protocol` (`Notifier`). The `Alerts` creator calls `make_notifier()` inside `alert()`; `EmailAlerts` and `SmsAlerts` override only that hook. The example also shows the lighter form: a registry dict plus `make_notifier(kind)`. Gotcha: raise `NotImplementedError` (or use `abc.ABC`) in the base hook so a missing override fails loudly, and never use `if/elif` on type strings in more than one place.

**Consequences** — Adding a product needs one new class and no client edits. Cost: an extra subclass per product in the class form.

**Related patterns** — **Abstract Factory** for families of products; **Template Method** is what the creator's workflow is; **Prototype** creates by cloning instead.
