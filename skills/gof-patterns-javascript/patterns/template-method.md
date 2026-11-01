# Template Method

Fixes the skeleton of an algorithm in a base class and lets subclasses supply individual steps.

Refs: https://github.com/HowProgrammingWorks/TemplateMethod  
Example: [examples/template-method.js](../examples/template-method.js)

**Intent** — Define the steps of an algorithm once and defer some of them to subclasses without changing the order.

**Problem** — Several variants (CSV, Markdown, JSON export) repeat the same flow and differ in a couple of steps.

**Applicability** — **Use** when the order is fixed and the variation is a few hooks. **Avoid** a class hierarchy when the steps can be passed as functions: a function taking `{ header, row }` (Strategy) is enough and composes better.

**JS implementation** — `Exporter.export` is the template: it calls `header` and `row`, and writes each row's values in header order (`columns.map((c) => r[c])`) so rows with another key order still line up. `CsvExporter` overrides `row`; `MarkdownExporter` overrides `row` and extends `header` through `super.header`. The abstract step throws in the base class so an unfinished subclass fails loudly. A functional form is `const exporter = ({ header, row }) => (rows) => ...`. Gotcha: an overridable method called from the base constructor runs before subclass fields are initialized.

**Consequences** — No duplicated flow and one place to change the order; inheritance couples subclasses to the base class, and the skeleton can be hard to follow.

**Related patterns** — **Strategy** for the composition-based alternative; **Factory Method** is often one step of a template; **Decorator** adds behavior without subclassing.
