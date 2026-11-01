# Composite

A tree where leaves and branches share one type, modelled in Swift with an `indirect enum` or a protocol.

Refs: https://refactoring.guru/design-patterns/composite/swift/example
Example: [examples/composite.swift](../examples/composite.swift)

**Intent** — Compose objects into trees and treat single objects and groups uniformly.

**Problem** — Files and folders, menus, or UI view hierarchies need the same operations (size, render) at every level.

**Applicability** — **Use** when the domain is naturally recursive and clients should not care whether they hold a leaf or a group. **Avoid** a component protocol with leaf and group types when the structure is flat or the tree is closed: an array, or an enum with indirect cases, is enough.

**Swift implementation** — Use `indirect enum FileNode` with `file` and `folder` cases and recursive computed properties and functions, as the example's `totalBytes` and `outline` do. When nodes must be open to new kinds, use a protocol with a struct leaf and a struct composite holding `[any Node]`. Use classes only if nodes need identity or parent links. SwiftUI's view tree is a composite.

**Consequences** — Uniform recursion and simple client code. Type-safety of leaf-only operations is weaker when a protocol is used.

**Related patterns** — **Visitor** runs operations over a composite; **Iterator** traverses it; **Decorator** has the same recursive shape with one child; **Builder** assembles it.
