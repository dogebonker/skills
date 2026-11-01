# Observer

A `Vec<(usize, Box<dyn Fn(&Event)>)>` of closure subscribers called by `publish`.

Refs: https://refactoring.guru/design-patterns/observer/rust/example
Example: [examples/observer.rs](../examples/observer.rs)

**Intent** — Let objects subscribe to events from another object and be called when it changes.

**Problem** — An account must feed an audit log and raise alerts without knowing about either.

**Applicability** — **Use** when one change should trigger several independent reactions. **Avoid** a subscriber list when one consumer needs updates: take a closure or use an `mpsc` channel; `tokio::sync::broadcast` covers async fan-out.

**Rust implementation** — `Account` stores `subscribers: Vec<(usize, Box<dyn Fn(&Event)>)>` and `subscribe(impl Fn(&Event) + 'static) -> usize`, which returns an id that `unsubscribe(id)` removes with `retain` (a repeated call is harmless). `withdraw` returns `Result` and publishes only on success. An enum `Event` replaces a notification class hierarchy. When subscribers need to write shared state, as the audit log does here, `Rc<RefCell<..>>` is the unavoidable cost of several owners mutating on one thread; use `Arc<Mutex<..>>` across threads. Hold `Weak` references if subscribers can disappear. The gotcha: a subscriber that calls back into the subject while it is being iterated will fail to borrow.

**Consequences** — Loose coupling and open-ended subscribers. The cost is hard-to-trace flow and lifetime leaks if nothing unsubscribes.

**Related patterns** — **Mediator** for two-way coordination; **Command** for events as stored actions; **Chain of Responsibility** for events where only one handler acts.
