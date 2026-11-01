# One Way to Do It

Give each common task one obvious way in the codebase, and remove the alternatives.

Refs: https://peps.python.org/pep-0020/
Example: [examples/one-way-to-do-it.ts](../examples/one-way-to-do-it.ts)

**Principle** — The Zen of Python (PEP 20, Tim Peters) says there should be one, and preferably only one, obvious way to do it. In a codebase, each extra way to read config, log, make HTTP calls or format money is something every reader must learn and every reviewer must check for agreement. Alternatives drift: one path gets a fix or a default the others miss.

**Violation signals** — Several accessors over the same data (`settings.get("HTTP_TIMEOUT_MS")`, `settings.timeoutMs`, `getSetting(...)`). Two HTTP clients, two date libraries or two logging setups in one service. Helpers that wrap the same call with different names. A half-finished migration with old and new APIs both in use.

**Fix** — Pick one way, migrate callers, delete the rest. In the example a single `config` object, parsed once with typed fields (`config.httpTimeoutMs`), replaces the three accessors. Enforce it with a lint rule or a restricted import where the toolchain allows.

**When not to apply** — Different needs can justify different tools (a streaming parser beside `JSON.parse` for huge files); document why. During a migration two ways coexist briefly, with a deadline. PEP 20's own next line admits the obvious way may not be obvious at first: write it down.

**Related** — **Facade** (`gof-patterns-typescript/patterns/facade.md`) for one entry point over a subsystem; **Singleton** (`gof-patterns-typescript/patterns/singleton.md`) for a module-level config object; [`boring-technology`](boring-technology.md); [`single-source-of-truth`](../../dry-patterns/patterns/single-source-of-truth.md).
