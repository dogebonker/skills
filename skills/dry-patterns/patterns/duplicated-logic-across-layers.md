# Duplicated Logic Across Layers

Write validation and business rules once and run the same definition on the client and the server.

Refs: https://json-schema.org/overview/what-is-jsonschema
Example: [examples/duplicated-logic-across-layers.ts](../examples/duplicated-logic-across-layers.ts)

**Principle** — A rule such as "password at least 12 characters" is one piece of knowledge, even when the form, the API handler and the database all enforce it. Each hand-written copy drifts on its own schedule, and users see the form accept what the server rejects. Declarative schemas such as JSON Schema exist so that many tools and languages can check data against one definition.

**Violation signals** — The same regex or length check in a React form and in a request handler. Error messages with the same meaning but different wording per layer. A rule change that needs PRs to two repositories.

**Fix** — Move the rule into one declaration both layers import. In the example, `signupSchema` lists rules as data and `validate()` reads them; `clientValidate` and `serverHandle` both call it. Across languages, share a JSON Schema or OpenAPI document and generate or load validators from it. The server still validates: the client check is a convenience, the server check is the boundary.

**When not to apply** — Rules that need server-only data (unique email, stock levels) stay on the server; do not ship them to the client.

**Related** — **Adapter** (`gof-patterns-typescript/patterns/adapter.md`) to turn schema errors into each layer's format; [`single-source-of-truth`](single-source-of-truth.md); [`generate-dont-repeat`](generate-dont-repeat.md); [`rule-of-least-power`](../../kiss-patterns/patterns/rule-of-least-power.md) for keeping rules as data.
