---
name: solid-patterns-typescript
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in TypeScript, read through structural typing. Use when designing or refactoring TypeScript modules, classes or interfaces against SOLID, or when deciding between an interface, a union and a function type."
---

# SOLID in TypeScript

- Apply a principle only where its symptom shows: an axis that really changes, a second implementation, a client that really needs less. Otherwise the plain version wins.
- The unit is usually a module or a function, not a class. A pure exported function already has one responsibility and needs no wrapper.
- Structural typing means implementers need no `implements` and consumers can name the exact slice they use (`Pick<T, "m">` or a local interface).
- Extension points are function types and records of functions checked with `satisfies`; a closed set you own is better as a discriminated union with an exhaustive `switch`.
- tsc checks shape, not behaviour: an override that throws or ignores input still compiles. Method shorthand parameters stay bivariant even under `strictFunctionTypes`; declare callbacks as properties to get contravariant checks.
- Inject dependencies through constructor or function parameters and wire them in one composition root; a DI container is optional.
- Use `#private` fields and explicit constructor fields so examples also run under Node's type stripping.

## How to use

Each entry has `patterns/<id>.md` and `examples/<id>.ts`, where `<id>` is the short id in the list (`srp`). Read the pattern file and its example before designing, reviewing or refactoring against that principle. Each example holds the violation and the fix side by side and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a change.

## Principles
- **Single Responsibility** (`srp`): a module mixes concerns that different people change, such as tax maths, layout and storage.
- **Open/Closed** (`ocp`): every new variant edits the same `switch`; move the variants into a table of functions.
- **Liskov Substitution** (`lsp`): a subtype throws, ignores input or needs `instanceof` checks where callers expect the base contract.
- **Interface Segregation** (`isp`): a function takes a wide interface and uses one member, so fakes fill up with unused stubs.
- **Dependency Inversion** (`dip`): domain code constructs or imports its own database, HTTP or messaging client.
