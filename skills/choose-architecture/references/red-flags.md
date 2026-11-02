# System red flags

Check each candidate against every flag. A hit counts against the candidate unless a stated force justifies it, in which case record the force and keep the flag visible in the output. The bracket names the owning book file.

## Boundaries

- **Distributed monolith**: deployables that must release together, or share one schema. [domain-driven-design-distilled]
- **Unenforced modules**: a monolith whose modules read each other's tables or call each other's internals, with no CI check on module seams. [domain-driven-design-distilled]
- **Split by technical layer**: services such as "frontend service", "logic service" and "database service" instead of business capabilities. [domain-driven-design-distilled]
- **One model across separate concerns**: billing, identity, catalog or permissions sharing domain classes or tables instead of translating at the boundary. [domain-driven-design-distilled]
- **Ceremony on generic parts**: separate services or full tactical DDD for a Generic or Supporting subdomain with no complexity force behind it. [domain-driven-design-distilled]
- **More deployables than the team can run**: count the services, stores and queues against team size and on-call capacity. [release-it]

## Interfaces

- **Shallow service**: an API about as complex as what it hides, or one that forwards calls to another. [a-philosophy-of-software-design]
- **Leaky contract**: callers must know call order, storage layout, caching or internal workflow to use a boundary. [a-philosophy-of-software-design]
- **Chatty remote calls**: one user action needs many sequential calls across a process boundary. Prefer one coarse use-case call. [patterns-of-enterprise-application-architecture]
- **Framework-shaped core**: ORM rows, vendor SDK types or transport payloads used as the domain model. [clean-architecture]

## Data

- **No single writer**: two deployables write the same data, or nobody can name its source of truth. [designing-data-intensive-applications]
- **Dual write**: a store write and an event publish with no outbox, change data capture or other atomic link. [designing-data-intensive-applications]
- **Exactly-once assumption**: retries, queues or consumers without idempotency and duplicate handling. [designing-data-intensive-applications]
- **Orphan copy**: a cache, read model, search index or replica without an owner, a staleness bound and a rebuild path. [designing-data-intensive-applications]
- **Unmapped weak consistency**: eventual consistency or a weak isolation level on data the Consistency force marks as never wrong. [designing-data-intensive-applications]

## Failure

- **Unguarded remote call**: an outbound call without a timeout, bounded retries and a degraded mode. [release-it]
- **Unbounded resource**: a queue, pool, buffer or list endpoint with no capacity limit or defined behaviour when full. [release-it]
- **Cascading dependency**: one slow dependency can exhaust threads or connections shared with unrelated paths. [release-it]
- **Hollow health check**: a health signal that passes while the component cannot actually serve. [release-it]

## LLM components

- **LLM doing rule work**: a model making authorization, policy or rule decisions, or handling a task with clear rules and structured inputs. [references/ai-systems.md]
- **Agent where a workflow fits**: open-ended autonomy for steps that are known in advance. [references/ai-systems.md]
- **Unvalidated output**: model output crossing a boundary without schema validation. [references/ai-systems.md]
- **Trusted untrusted input**: retrieved or user content can steer a model that holds write tools or irreversible actions without human approval. [references/ai-systems.md]
- **No eval before build**: the LLM part has no offline test set and quality bar defined ahead of implementation. [references/ai-systems.md]

## Migration (brownfield only)

- **Big-bang rewrite**: the target goes live in one cutover, with no step that ships on its own. [working-effectively-with-legacy-code]
- **Target without pain**: the change removes no pain that has evidence. [working-effectively-with-legacy-code]
- **Step without rollback**: a migration step that cannot be undone, or has no observable done signal. [release-it]
- **Migration dual write**: application code writes both the old and the new store while data moves. [designing-data-intensive-applications]
- **Unprotected seam**: a step moves a seam that has no characterization tests. [working-effectively-with-legacy-code]
- **Endless strangler**: two live paths with no end date. [working-effectively-with-legacy-code]
