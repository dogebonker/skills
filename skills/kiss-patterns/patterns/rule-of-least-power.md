# Rule of Least Power

Express rules, configuration and content in the least powerful language that can say them: data before a DSL, a DSL before general code.

Refs: https://www.w3.org/2001/tag/doc/leastPower.html
Example: [examples/rule-of-least-power.ts](../examples/rule-of-least-power.ts)

**Principle** — The W3C TAG finding (Berners-Lee and Mendelsohn, 2006) advises using the least powerful language suitable for the information. Declarative data can be analysed, indexed, validated and reused by tools that never run it. A Turing-complete program can often only be understood by running it, and it is harder to secure.

**Violation signals** — `eval`, `new Function` or `exec` over strings from config or a database. Business rules as JavaScript or Python snippets in an admin field. Templates with arbitrary code where simple variable substitution would do. Build or config files that are programs when a static list would serve.

**Fix** — Turn each rule into a typed record and write one small interpreter. In the example `ruleSources` code strings become `DiscountRule` values (`percentOverTotal`, `flatOverItems`) read by `applyRule()`. The admin UI can now list, validate and diff them, and a `never`-checked `switch` catches new kinds.

**When not to apply** — The language must still be powerful enough. When the data form grows conditionals, loops and variables, you are building a worse programming language: use real code with tests. Plugins written by trusted developers can be code.

**Related** — **Command** (`gof-patterns-typescript/patterns/command.md`) for actions stored as values; **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) when a rule really needs code; [`data-over-code`](data-over-code.md); [`duplicated-logic-across-layers`](../../dry-patterns/patterns/duplicated-logic-across-layers.md) for schemas shared as data.
