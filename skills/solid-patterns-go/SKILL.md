---
name: solid-patterns-go
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in Go, read through small consumer-defined interfaces. Use when designing or refactoring Go packages, interfaces or dependencies against SOLID, or when deciding whether an interface earns its cost."
---

# SOLID in Go

- Read SOLID through packages, functions and interfaces; Go has no classes or inheritance, so the class-centric wording translates rather than applies.
- Name packages for what they provide (`billing`, `report`); a `utils` or `common` package is a single-responsibility smell.
- Define small interfaces in the package that consumes them; types satisfy them implicitly, so the producer needs no change.
- Return concrete types from constructors, unless the constructor picks the type at runtime (Factory Method), and accept interfaces as parameters.
- Treat an interface's documented behavior as its contract: "require no more, promise no less" (Cheney). A method that always errors or panics breaks substitution.
- Use embedding to reuse methods, not to override them: the embedded type never calls back into the outer one.
- Push concrete choices (database, mail transport, HTTP client) up to `main`, and keep the import graph wide, flat and acyclic.
- Add an interface when a second implementation or a real consumer boundary exists; one implementation behind an interface "for mocking" is overuse.

## How to use

Pick the principle from the index, then read its pattern file and its example before designing, reviewing or refactoring. Each entry has `patterns/<id>.md` and `examples/<id>.go`; the example shows the violation and the fix in one file and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a split or an interface.

## Principles
- **Single Responsibility** (`srp`): a package or function changes for more than one reason, or a `utils` package collects unrelated code.
- **Open/Closed** (`ocp`): a `switch` on a kind or format grows a case with every feature.
- **Liskov Substitution** (`lsp`): an implementation refuses or weakens an interface method, and callers type-assert to work around it.
- **Interface Segregation** (`isp`): a function takes a wide interface or `*os.File` but uses one method.
- **Dependency Inversion** (`dip`): business code constructs or imports its database, SDK or transport directly.
