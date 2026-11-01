---
name: dry-patterns
description: "Reference for DRY (don't repeat yourself) and its limits: single source of truth, rule of three, wrong abstraction, magic values, normalization, DAMP tests. Use when applying or explaining DRY, or deciding whether to extract shared code."
---

# DRY Patterns

- DRY is about knowledge: each business rule, schema or decision has one authoritative home. Similar-looking text is not duplication unless it encodes the same fact.
- Ask "if this changes, must the other copy change too?" Merge only when the answer is yes.
- Derive types, validators, UI options and docs from one declaration, or generate them from a spec.
- Tolerate a second copy of similar code; extract on the third, and extract only what all copies share. A copied business rule gets one owner at once.
- Duplication is cheaper than the wrong abstraction. When a shared function grows a flag per caller, inline it and start again.
- Name unexplained literals, and store each persisted fact once.
- Tests favour readable repetition (DAMP): each test shows its own inputs, helpers supply defaults.

## How to use

Pick the entry from the index, then read its pattern file and its example before refactoring, explaining or reviewing. Each entry has `patterns/<id>.md` and `examples/<id>.<ext>` (`.ts` or `.py`, named in the index), where `<id>` is the kebab-case name shown in the list. Each example puts the violation and the fix side by side and prints both behaving the same. Take idioms from the example, and follow the codebase's own naming and structure; the domain names in examples are only illustrations. GoF links point at `gof-patterns-typescript` and SOLID links at `solid-patterns-typescript`; the same `<id>` exists in the skill for the codebase's language. Read only the entries the task needs.

## Index
- **Knowledge, Not Text** (`knowledge-not-text`): deciding whether two similar fragments are real duplication or a coincidence. Example: Python.
- **Single Source of Truth** (`single-source-of-truth`): a list, constant or setting is written in several places that must agree. Example: TypeScript.
- **Rule of Three** (`rule-of-three`): deciding when to extract repeated code. Example: Python.
- **Wrong Abstraction** (`wrong-abstraction`): a shared function or class has grown flags and branches per caller. Example: TypeScript.
- **Duplicated Logic Across Layers** (`duplicated-logic-across-layers`): client, server or database each re-implement the same validation or rule. Example: TypeScript.
- **Generate, Don't Repeat** (`generate-dont-repeat`): field lists are retyped across models, parsers, clients and docs. Example: Python.
- **Parallel Hierarchies** (`parallel-hierarchies`): adding a subclass in one tree forces a matching subclass in another. Example: TypeScript.
- **Magic Values** (`magic-values`): unexplained numbers or strings in conditions, durations or status checks. Example: Python.
- **Tests: DAMP over DRY** (`test-damp-vs-dry`): test helpers or tables hide what each test checks. Example: Python.
- **Data Normalization** (`data-normalization`): the same fact is stored on many records and updates must touch every copy. Example: TypeScript.
