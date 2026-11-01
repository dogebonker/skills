# Single Responsibility (SRP)

Keep together the code that changes for the same reason, and separate code that changes for different reasons.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
Example: [examples/srp.swift](../examples/srp.swift)

**Principle** — Martin defines a responsibility as a reason to change, and later as the group of people who request it. In Swift the unit is a type or a module. Extensions split a type's code across files, but the type is still one unit that every change touches, so moving methods into `extension ReceiptManager` does not separate responsibilities.

**Violation signals** — `Manager`, `Helper` or `Service` classes with unrelated methods, as `ReceiptManagerV1.process` totals, formats and archives in one call. Massive view controllers that fetch, parse, format and lay out.

**Fix** — Small value types with one job each: `ReceiptCalculator` (tax rule), `ReceiptFormatter` (text and currency), `ReceiptArchive` (storage). Compose them at the call site or in a coordinator. Moving a type into its own module makes the boundary visible to the compiler through `internal` and `public`.

**When not to apply** — One type per function, or a protocol per type, for logic one person changes together. A `struct` with a few cohesive methods is fine, and SwiftUI views legitimately combine layout and small view logic. Split when two reasons to change are real, not imagined.

**Related** — **Facade** (`gof-patterns-swift/patterns/facade.md`) for one entry point over the split types; **Strategy** (`gof-patterns-swift/patterns/strategy.md`) for passing a rule in as a closure; **ISP** ([isp.md](isp.md)) for the same split seen from callers; **Speculative generality** (`kiss-patterns/patterns/speculative-generality.md`) for the overuse case.
