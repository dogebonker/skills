# Flyweight

Saves memory allocation by sharing common state among multiple instances.

Refs: https://github.com/HowProgrammingWorks/Flyweight  
Example: [examples/flyweight.js](../examples/flyweight.js)

**Intent** — Split intrinsic (shared, immutable) from extrinsic (per-instance) data so many light “views” point at few shared flyweights.

**Problem** — Huge collections of near-duplicate objects (text, tiles, icons) blow memory if every cell owns a full copy.

**Applicability** — **Use** when intrinsic keys are enumerable and extrinsic state stays outside the flyweight. **Avoid** a flyweight cache when objects need their own identity or mutable state: plain per-instance objects are enough.

**Preconditions** — Intrinsics should be frozen or readonly; extrinsics live on the wrapper object (`row`, `col` in the example).

**JS implementation** — `Map` key -> frozen object. `getFlyweight` builds the key from the intrinsic fields and stores only those fields, so extra input properties never leak into the shared object; `createChar` adds the extrinsic `row` and `col`. Gotcha: the pool never evicts, so unbounded keys grow memory; add an LRU limit when keys come from input.

**Consequences** — Large wins for dense data; key design dominates correctness and eviction policy if needed.

**Related patterns** — **Prototype** for cheap unshared copies; **Object Pool** recycles mutable handles instead of sharing immutable data.
