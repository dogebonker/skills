# Bridge

Separates two or more abstraction hierarchies via composition or aggregation, allowing them to evolve independently.

Refs: https://github.com/HowProgrammingWorks/Bridge  
Example: [examples/bridge.js](../examples/bridge.js)

**Intent** — Let feature hierarchy (devices) vary separately from implementation hierarchy (protocols).

**Problem** — Cartesian product of `SmartLight×MQTT`, `SmartLight×HTTP`, … explodes without composition.

**Applicability** — **Use** when both dimensions change often. **Avoid** a bridge when one dimension is fixed: a single injected strategy is enough.

**Participants / collaboration** — Device holds `protocol`; operations delegate `sendCommand(name, payload)` without knowing transport details.

**JS implementation** — Inject the protocol instance through the constructor; device subclasses call `operate`, which delegates to `protocol.sendCommand`. See the IoT example. Gotcha: the base `CommunicationProtocol.sendCommand` throws, so a protocol that forgets to override it fails at the first command, not at construction.

**Consequences** — Two small hierarchies instead of one wide one; wiring happens at composition root (app/bootstrap).

**Related patterns** — **Strategy** for the degenerate bridge with one abstraction; **Adapter** wraps a protocol whose interface is foreign.
