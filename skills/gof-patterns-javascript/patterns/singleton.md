# Singleton

Provides global access to a single instance; often considered an anti-pattern, easiest implemented via ESM/CJS module caching exported refs.

Refs: https://github.com/HowProgrammingWorks/Singleton  
Example: [examples/singleton.js](../examples/singleton.js)

**Intent** — Guarantee one shared coordinator or state bag for the process (or module graph).

**Problem** — Multiple instances would break coordination (rate limits, connection pool, legacy APIs).

**Applicability** — **Use** sparingly: module-scope maps, log sinks, true OS-level single resources. **Avoid** a singleton when tests or parallel contexts need their own instance: passing it through parameters, context or DI is enough.

**JS implementation** — Prefer **module exports** (natural singleton in Node/ESM) over clever `IIFE` constructors unless legacy requires them. Example shows module state first, then class and closure variants with `null`-initialized instance. Gotcha: the module cache is keyed by resolved path, so two copies of a package in `node_modules` give two separate "singletons".

**Consequences** — Simple wiring; hides dependencies and complicates tests and hot reload unless you inject abstractions.

**Related patterns** — **Context** replaces a hidden singleton with an explicit parameter; **Multiton** for one instance per key.
