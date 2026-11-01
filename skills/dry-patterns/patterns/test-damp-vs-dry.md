# Tests: DAMP over DRY

In tests, prefer readable repetition: each test states its own inputs and expectation, and shared helpers only supply defaults.

Refs: https://abseil.io/resources/swe-book/html/ch12.html
Example: [examples/test-damp-vs-dry.py](../examples/test-damp-vs-dry.py)

**Principle** — Software Engineering at Google (chapter 12, "DAMP, not DRY") says test code should favour Descriptive And Meaningful Phrases: some duplication is fine when it makes a test simpler to read. A failing test must explain itself without tracing helpers. Kent C. Dodds' "AHA Testing" (https://kentcdodds.com/blog/aha-testing) describes the two extremes: full setup pasted into every test, and shared utilities with growing conditionals and nested `beforeEach`.

**Violation signals** — A table of positional tuples with boolean flags (`coupon_wins`) and a generic runner whose failure says `case 2`. Shared `setUp` that builds values a test silently depends on. Helpers with `if` branches per test.

**Fix** — Write one named test per behaviour and use a factory with defaults plus overrides (`make_order(coupon="WELCOME10")`) so each test shows only the values that matter. Keep focused helpers that build values or assert one fact. Use parametrized tests (`pytest.mark.parametrize`, `test.each`) for a pure function over many inputs when each row is readable on its own.

**When not to apply** — Repeated boilerplate that carries no meaning (server start-up, temp dirs) belongs in fixtures. Hundreds of near-identical input rows are clearer as a table than as hundreds of functions.

**Related** — **Builder** (`gof-patterns-typescript/patterns/builder.md`) for test data builders with defaults; [`wrong-abstraction`](wrong-abstraction.md) for helpers that grew flags; [`rule-of-three`](rule-of-three.md).
