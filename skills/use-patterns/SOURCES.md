# Sources

All text in this skill is written in its own words. Research notes were gathered on 2026-10-31. "Entries" below are `reference/catalog.md` headings unless a file is named.

## Joshua Kerievsky, Refactoring to Patterns (Addison-Wesley, 2004)

The book itself was not read. Its catalog names and one-line problem statements come from Industrial Logic's online catalog, and its framing from the draft preface.

| URL | Used by |
|---|---|
| https://industriallogic.com/xp/refactoring/catalog.html | catalog index: which refactorings exist and their names |
| https://industriallogic.com/refactoring-to-patterns/catalog/conditionalWithStrategy.html | Strategy |
| https://industriallogic.com/refactoring-to-patterns/catalog/alteringConditionalsWithState.html | State |
| https://industriallogic.com/refactoring-to-patterns/catalog/conditionDispatcherWithCommand.html | Command |
| https://industriallogic.com/refactoring-to-patterns/catalog/hardCodedNotificationsWithObserver.html | Observer |
| https://industriallogic.com/refactoring-to-patterns/catalog/polymorphicCreationFactory.html | Factory Method - Introduce Polymorphic Creation |
| https://industriallogic.com/refactoring-to-patterns/catalog/creationWithFactory.html | Factory Method - Move Creation Knowledge |
| https://industriallogic.com/refactoring-to-patterns/catalog/classesWithFactory.html | Factory Method - Move Creation Knowledge |
| https://industriallogic.com/refactoring-to-patterns/catalog/constructorCreation.html | Builder |
| https://industriallogic.com/refactoring-to-patterns/catalog/compositeWithBulder.html | Builder |
| https://industriallogic.com/refactoring-to-patterns/catalog/formTemplateMethod.html | Template Method |
| https://industriallogic.com/refactoring-to-patterns/catalog/embellishmentToDecorator.html | Decorator |
| https://industriallogic.com/refactoring-to-patterns/catalog/onemanyDistinctionsWithComposite.html | Composite |
| https://industriallogic.com/refactoring-to-patterns/catalog/implicitTreeWithComposite.html | Composite |
| https://industriallogic.com/refactoring-to-patterns/catalog/interfacesWithAdapter.html | Adapter |
| https://industriallogic.com/refactoring-to-patterns/catalog/extractAdapter.html | Adapter |
| https://industriallogic.com/refactoring-to-patterns/catalog/accumulationToVisitor.html | Visitor |
| https://industriallogic.com/refactoring-to-patterns/catalog/nullObject.html | Null Object |
| https://industriallogic.com/refactoring-to-patterns/catalog/instantiationWithSingleton.html | Singleton |
| https://industriallogic.com/refactoring-to-patterns/catalog/inlineSingleton.html | KISS - Pattern overuse: inline a singleton |
| https://courses.cs.duke.edu/compsci307d/current/readings/kerievsky_preface.pdf | SKILL.md Rules (under- and over-engineering both cost); Decorator (the 10-line class versus 50-line Decorator story); KISS - Pattern overuse: inline a singleton (Replace Singleton with Object Reference as a table-of-contents title) |
| https://ecs.syr.edu/faculty/fawcett/handouts/CSE776/presentations/RefactoringToPatterns.pdf | SKILL.md Rules and step 3 (refactoring to, towards and away from patterns) |
| https://www.jetbrains.com/help/idea/2023.2/replace-conditional-logic-with-strategy-pattern.html | Strategy steps, the one entry marked "Kerievsky, confirmed" (a worked walkthrough of the book's refactoring, not the book's numbering) |
| https://scrutinizer-ci.com/docs/refactorings/replace-conditional-dispatcher-with-command | Command steps, marked "confirmed secondhand" (seen through a search snippet; the page returned 403) |

## refactoring.guru

| URL | Used by |
|---|---|
| https://refactoring.guru/design-patterns/factory-method | Factory Method (both entries) |
| https://refactoring.guru/design-patterns/abstract-factory | Abstract Factory |
| https://refactoring.guru/design-patterns/builder | Builder |
| https://refactoring.guru/design-patterns/prototype | Prototype |
| https://refactoring.guru/design-patterns/singleton | Singleton; KISS - Pattern overuse: inline a singleton |
| https://refactoring.guru/design-patterns/adapter | Adapter |
| https://refactoring.guru/design-patterns/bridge | Bridge |
| https://refactoring.guru/design-patterns/composite | Composite |
| https://refactoring.guru/design-patterns/decorator | Decorator |
| https://refactoring.guru/design-patterns/facade | Facade |
| https://refactoring.guru/design-patterns/flyweight | Flyweight |
| https://refactoring.guru/design-patterns/proxy | Proxy |
| https://refactoring.guru/design-patterns/chain-of-responsibility | Chain of Responsibility |
| https://refactoring.guru/design-patterns/command | Command |
| https://refactoring.guru/design-patterns/iterator | Iterator |
| https://refactoring.guru/design-patterns/mediator | Mediator |
| https://refactoring.guru/design-patterns/memento | Memento |
| https://refactoring.guru/design-patterns/observer | Observer |
| https://refactoring.guru/design-patterns/state | State |
| https://refactoring.guru/design-patterns/strategy | Strategy |
| https://refactoring.guru/design-patterns/template-method | Template Method |
| https://refactoring.guru/design-patterns/visitor | Visitor |
| https://refactoring.guru/smells/switch-statements | Factory Method - Move Creation Knowledge (a switch inside the one factory stays); Strategy and State counter-signals |
| https://refactoring.guru/smells/long-parameter-list | Builder; Builder - Introduce Parameter Object |
| https://refactoring.guru/smells/duplicate-code | Template Method; DRY - Duplicated knowledge; DRY - Duplicated logic across layers; DRY - Duplicate code inside one function |
| https://refactoring.guru/smells/speculative-generality | KISS - Pattern overuse: collapse a one-implementation abstraction; KISS - Speculative generality |
| https://refactoring.guru/smells/lazy-class | KISS - Pattern overuse: collapse a one-implementation abstraction |
| https://refactoring.guru/smells/middle-man | KISS - Needless indirection; Facade counter-signal |
| https://refactoring.guru/smells/parallel-inheritance-hierarchies | Bridge (also DRY parallel hierarchies) |
| https://refactoring.guru/smells/alternative-classes-with-different-interfaces | Adapter |
| https://refactoring.guru/smells/temporary-field | Null Object |
| https://refactoring.guru/smells/inappropriate-intimacy | Mediator |
| https://refactoring.guru/replace-conditional-with-polymorphism | Strategy; SKILL.md step 4 |
| https://refactoring.guru/replace-type-code-with-state-strategy | State |
| https://refactoring.guru/replace-constructor-with-factory-method | Factory Method - Introduce Polymorphic Creation |
| https://refactoring.guru/form-template-method | Template Method |
| https://refactoring.guru/introduce-parameter-object | Builder; Builder - Introduce Parameter Object (steps marked "refactoring.guru, confirmed"); SKILL.md step 4 |
| https://refactoring.guru/smells/data-clumps | Builder - Introduce Parameter Object |
| https://refactoring.guru/preserve-whole-object | Builder - Introduce Parameter Object |
| https://refactoring.guru/consolidate-duplicate-conditional-fragments | DRY - Duplicate code inside one function (steps marked "refactoring.guru, confirmed") |
| https://refactoring.guru/extract-method | DRY - Duplicate code inside one function |
| https://refactoring.guru/smells/dead-code | KISS - Dead code |
| https://refactoring.guru/introduce-null-object | Null Object |
| https://refactoring.guru/remove-middle-man | KISS - Needless indirection |
| https://refactoring.guru/collapse-hierarchy | KISS - Pattern overuse: collapse a one-implementation abstraction |

## Martin Fowler, Sandi Metz and the rule of three

| URL | Used by |
|---|---|
| https://martinfowler.com/bliki/CodeSmell.html | SKILL.md Rules (a smell is a prompt to investigate) |
| https://martinfowler.com/bliki/FlagArgument.html | signals.md S4 (boolean flag parameters) |
| https://martinfowler.com/bliki/Yagni.html | KISS - Pattern overuse: collapse a one-implementation abstraction; KISS - Speculative generality; KISS - Dead code |
| https://martinfowler.com/bliki/BeckDesignRules.html | KISS - Dead code |
| https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction | DRY - Wrong abstraction (steps marked "Metz, confirmed") |
| https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming) | SKILL.md Rules; Template Method; DRY - Wrong abstraction; DRY - Duplicate code inside one function |
| https://en.wikipedia.org/wiki/Singleton_pattern | KISS - Pattern overuse: inline a singleton (hidden dependencies, testing cost) |

## Detection research and lint thresholds

| URL | Used by |
|---|---|
| https://sol.sbc.org.br/index.php/sbsi/article/view/6127 | Strategy counter-signal (a switch mapping strings to flags is not a Strategy opportunity) |
| https://www.cse.iitm.ac.in/~krishna/preprints/icse17-c/icse17-c.pdf | State (a type code tested in several methods; mutable after construction means State) |
| https://docs.pmd-code.org/latest/pmd_rules_java_design.html | signals.md numeric thresholds |
| https://eslint.org/docs/latest/rules/max-params | signals.md numeric thresholds; Builder |
| https://eslint.org/docs/latest/rules/complexity | signals.md numeric thresholds |
| https://typescript-eslint.io/rules/switch-exhaustiveness-check/ | signals.md numeric thresholds |

## Language idioms

| URL | Used by |
|---|---|
| https://norvig.com/design-patterns/design-patterns.pdf | "Idiom first" lines in general (patterns that first-class functions and types make simpler) |
| https://openjdk.org/jeps/441 | Visitor (exhaustive pattern matching as the alternative) |
| https://kotlinlang.org/docs/sealed-classes.html | Visitor and State (sealed types with exhaustive `when`) |
| https://rust-unofficial.github.io/patterns/patterns/behavioural/visitor.html | Visitor (when a Rust visitor still pays) |
| https://rust-unofficial.github.io/patterns/patterns/behavioural/strategy.html | Strategy (closures for small strategies in Rust) |
| https://docs.python.org/3/howto/functional.html | Iterator (generators) |
| https://nodejs.org/api/modules.html | Singleton (module caching makes a module-level instance shared) |

## Through the sibling skills

The DRY, KISS and SOLID entries point at the sibling skills' pattern files for detail. The URLs below are the ones those files cite in their `Refs` lines; this skill took them from there and did not fetch them itself.

| URL | Used by |
|---|---|
| https://en.wikipedia.org/wiki/Single_source_of_truth | DRY - Duplicated knowledge |
| https://www.artima.com/articles/orthogonality-and-the-dry-principle | DRY - Duplicated knowledge (knowledge, not text) |
| https://json-schema.org/overview/what-is-jsonschema | DRY - Duplicated logic across layers |
| https://refactoring.guru/replace-magic-number-with-symbolic-constant | DRY - Magic values |
| https://refactoring.guru/replace-nested-conditional-with-guard-clauses | KISS - Nested conditionals |
| https://doi.org/10.1145/356635.356640 | KISS - Premature optimization |
| http://www.catb.org/esr/writings/taoup/html/ch01s06.html | KISS - Data over code |
| https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html | SOLID - SRP |
| https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html | SOLID - OCP |
| https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf | SOLID - LSP |
| https://cs.utexas.edu/~downing/papers/ISP-1996.pdf | SOLID - ISP |
| https://cs.utexas.edu/~downing/papers/DIP-1996.pdf | SOLID - DIP |

From the original refactoring.guru research notes: https://refactoring.guru/smells/large-class (SOLID - SRP) and https://refactoring.guru/smells/refused-bequest (SOLID - LSP).

## Skills this one hands off to

- `~/.claude/skills/gof-patterns-{javascript,typescript,go,rust,kotlin,swift,python}/`: GoF target shapes.
- `~/.claude/skills/dry-patterns/` and `~/.claude/skills/kiss-patterns/`: DRY and KISS target files (examples in TypeScript or Python).
- `~/.claude/skills/solid-patterns-{javascript,typescript,go,rust,kotlin,swift,python}/`: SOLID target files.
- `~/.claude/skills/refactoring-guru/`: small-step mechanics for step 6 and the KISS removal entries.

## Gaps

- Kerievsky's mechanics were confirmed for two entries only (Strategy, Command). Every other step list is marked "derived sketch".
- Fowler's full second-edition smell list and SonarSource default thresholds were not confirmed, so neither is used.
- Null Object has no gof-patterns file; its entry describes the target shape directly.
- The DRY, KISS and SOLID steps are all derived sketches except DRY - Wrong abstraction (Metz) and part of DRY - Duplicate code inside one function (refactoring.guru, read 2026-11-01). The Introduce Parameter Object, Consolidate Duplicate Conditional Fragments and Dead Code pages were read on 2026-11-01. Their principle sources come through the sibling skills and were not re-read here.
