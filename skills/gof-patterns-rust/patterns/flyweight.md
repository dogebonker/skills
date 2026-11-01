# Flyweight

Intrinsic state behind `Rc` (or `Arc`) held in a cache; extrinsic state stored per object.

Refs: https://refactoring.guru/design-patterns/flyweight/rust/example
Example: [examples/flyweight.rs](../examples/flyweight.rs)

**Intent** — Reduce memory by sharing the part of state that is identical across many objects.

**Problem** — A forest of thousands of trees each carrying the same large sprite bitmap.

**Applicability** — **Use** when many objects repeat large, immutable data. **Avoid** a flyweight cache when the data is small, `&'static` or `Copy`: a reference or copy is enough, and `Rc<str>` is a lighter way to intern strings.

**Rust implementation** — `SpriteCache` maps names to `Rc<Sprite>`, looking up with `get(name)` first so a hit allocates no key and inserting with `name.to_string()` only on a miss, and every `Tree` stores a cloned `Rc` plus its own `x` and `y`. `Rc::clone` bumps a counter and copies no pixels. Use `Arc` across threads. Shared data must be immutable, since `Rc` gives only shared references. The gotcha: if flyweights need mutation, you drift into `Rc<RefCell<..>>`, which breaks the pattern's premise. Separate the mutable part into the per-object state instead.

**Consequences** — Large memory savings. The cost is a cache to manage and the discipline to keep shared state immutable.

**Related patterns** — **Singleton** is one instance, where Flyweight has one per key; **Composite** has leaves that are often flyweights; **Prototype** for copies instead of sharing.
