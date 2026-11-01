# Template Method

A base class fixes an algorithm's skeleton and lets subclasses override specific steps.

Refs: https://refactoring.guru/design-patterns/template-method/python/example
Example: [examples/template-method.py](../examples/template-method.py)

**Intent** — Define the steps of an algorithm once, deferring some to subclasses.

**Problem** — Several importers share parse-validate-finish flow but differ in parsing and validation.

**Applicability** — **Use** when variants share one overall sequence and differ in a few steps. **Avoid** inheritance when you can pass functions in (Strategy), or when a `contextmanager` fits a "setup, body, teardown" shape: `import_job` wraps caller code with fixed start and end steps.

**Python implementation** — `Importer(ABC)` has `run` as the template, an `@abstractmethod parse`, a hook with a default (`is_valid`) and an empty optional hook (`after_import`). `CsvImporter` overrides `parse` and `is_valid`. The ABC prevents instantiating an incomplete subclass. Do not override `run` in subclasses; document it. Gotcha: hooks called from the template make subclass bugs surface far from their cause, so keep the step list short and named clearly.

**Consequences** — Removes duplication and centralises the flow. Cost: tied to inheritance and a fixed skeleton.

**Related patterns** — **Strategy** swaps whole algorithms via composition; **Factory Method** is a template method specialised for creation; **Decorator** alters behavior from outside.
