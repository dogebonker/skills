---
name: kiss-patterns
description: "Reference for KISS (keep it simple): YAGNI, speculative generality, simple design rules, least power, guard clauses, boring technology, premature optimization, pattern overuse. Use when simplifying a design or choosing the smallest one that meets a requirement."
---

# KISS Patterns

- Build for today's requirement; add a capability when a real need arrives, and keep code easy to change so that later addition is cheap.
- Simple means one concern, not intertwined; easy means familiar. Prefer simple.
- Follow Beck's rules in order: passes the tests, reveals intention, no duplication, fewest elements.
- Reach for the standard library, the platform and the tools already in production before writing or adding anything.
- Put knowledge in data: tables over branch ladders, declarative rules over code strings.
- Keep control flow flat: guard clauses first, normal path last.
- Measure before optimizing, and delete dead code before adding new code.
- Add a pattern, interface or factory only when the problem it solves exists in the code today.

## How to use

Pick the entry from the index, then read its pattern file and its example before simplifying, explaining or reviewing. Each entry has `patterns/<id>.md` and `examples/<id>.<ext>` (`.ts` or `.py`, named in the index), where `<id>` is the kebab-case name shown in the list. Each example puts the violation and the fix side by side and prints both behaving the same. Take idioms from the example, and follow the codebase's own naming and structure; the domain names in examples are only illustrations. Every pattern file has a "When not to apply" section: check it before removing anything. GoF links point at `gof-patterns-typescript` and SOLID links at `solid-patterns-typescript`; the same `<id>` exists in the skill for the codebase's language. Read only the entries the task needs.

## Index
- **YAGNI** (`yagni`): code, types or options exist for features the product does not have. Example: TypeScript.
- **Speculative Generality** (`speculative-generality`): unused hooks, parameters, base classes or delegation. Example: Python.
- **Smallest Thing That Works** (`smallest-thing-that-works`): a design is larger than the tests and the requirement need. Example: Python.
- **Rule of Least Power** (`rule-of-least-power`): rules or config are stored as executable code instead of data. Example: TypeScript.
- **Data Over Code** (`data-over-code`): an `if`/`switch` ladder only maps inputs to values. Example: Python.
- **Flat Over Nested** (`flat-over-nested`): deeply nested conditionals hide the normal path. Example: TypeScript.
- **Boring Technology** (`boring-technology`): someone proposes a new datastore, service, dependency or home-made format. Example: Python.
- **Premature Optimization** (`premature-optimization`): clever speed-ups or caches without a measurement. Example: Python.
- **One Way to Do It** (`one-way-to-do-it`): several APIs, helpers or libraries do the same job in one codebase. Example: TypeScript.
- **Delete Before Adding** (`delete-before-adding`): a feature lands next to dead flags, branches or functions. Example: Python.
- **Pattern Overuse** (`pattern-overuse`): single-implementation interfaces, single-product factories or needless singletons. Example: TypeScript.
