---
name: solid-patterns-python
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in Python, read through duck typing and typing.Protocol. Use when designing or refactoring Python modules, classes or protocols against SOLID, or when deciding whether a Protocol earns its cost."
---

# SOLID in Python

- Apply a principle only where its symptom shows: an axis that really changes, a second implementation, a client that really needs less. Otherwise the plain version wins.
- The module is the unit. Module-level functions carry one responsibility without a class; use a class only for state.
- Describe contracts with `typing.Protocol` declared next to the consumer; implementers satisfy it implicitly. Use `abc.ABC` only when you want incomplete subclasses to fail at instantiation.
- Duck typing makes LSP a behavioural contract: same accepted arguments, same return shape, no new exceptions. mypy checks signatures of overrides and protocol members, never behaviour.
- Extension points are mappings of callables, `functools.singledispatch` and plugin registries, rarely subclasses.
- Inject dependencies through `__init__` or function arguments and build them in one composition root; avoid `mock.patch` as the only seam.
- Examples target Python 3.10, run with `python3 -I`, and pass `mypy --strict`.

## How to use

Each entry has `patterns/<id>.md` and `examples/<id>.py`, where `<id>` is the short id in the list (`srp`). Read the pattern file and its example before designing, reviewing or refactoring against that principle. Each example holds the violation and the fix side by side and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a change.

## Principles
- **Single Responsibility** (`srp`): a class or module mixes concerns that different people change, such as tax maths, layout and storage.
- **Open/Closed** (`ocp`): every new variant edits the same `if/elif` or `match`; move the variants into a mapping of callables.
- **Liskov Substitution** (`lsp`): a subclass or protocol implementation raises, ignores input or needs `isinstance` checks.
- **Interface Segregation** (`isp`): a function is annotated with a wide ABC or class and calls one method of it.
- **Dependency Inversion** (`dip`): domain code constructs or imports its own database, HTTP or messaging client.
