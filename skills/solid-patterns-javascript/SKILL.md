---
name: solid-patterns-javascript
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in JavaScript, read through duck typing, functions and modules. Use when designing or refactoring JavaScript modules, classes or objects against SOLID, or when deciding whether a dependency or extension point earns its cost."
---

# SOLID in JavaScript

- Apply a principle only where its symptom shows: an axis that really changes, a second implementation, a client that really needs less. Otherwise the plain version wins.
- The unit is a module or a function. Most SOLID refactors in JavaScript end in plain functions and closures, not class hierarchies.
- Contracts are implicit under duck typing: method names, argument handling, return shape and thrown errors are what callers depend on, so substitutes must match all of them.
- Extension points are functions, objects or `Map`s of functions, and plugin arrays; guard keys from input with `Object.hasOwn`.
- A function's interface is its parameters: destructure exactly what it uses instead of passing `app`, `ctx` or service bags.
- Pass dependencies in as parameters or factory arguments (`createX(deps)`) and wire them in one composition root; avoid `jest.mock` as the only seam.
- Examples are CommonJS and print a demo under `if (require.main === module)`.

## How to use

Each entry has `patterns/<id>.md` and `examples/<id>.js`, where `<id>` is the short id in the list (`srp`). Read the pattern file and its example before designing, reviewing or refactoring against that principle. Each example holds the violation and the fix side by side and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a change.

## Principles
- **Single Responsibility** (`srp`): a module mixes concerns that different people change, such as tax maths, layout and storage.
- **Open/Closed** (`ocp`): every new variant edits the same `switch`; move the variants into an object of functions.
- **Liskov Substitution** (`lsp`): an object passed as a substitute throws, ignores input or needs `instanceof` checks.
- **Interface Segregation** (`isp`): a function takes an `app` or context bag and reaches through it for one or two members.
- **Dependency Inversion** (`dip`): domain code calls a module-level database, HTTP or messaging client directly.
