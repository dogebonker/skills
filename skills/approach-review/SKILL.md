---
name: approach-review
description: "Review architectural guarantees before local code details: shared lifecycle and public state contracts, recurring reads, transaction/lock coordination, security-control ownership, and asynchronous pipelines or extra infrastructure. Trace actual writers, competing actors and enforcement boundaries; test the design against its stated outcome."
---

# Approach Review

Review whether the design can keep its promises with justified ownership and
coordination. A sound approach is a valid result. Reviews are read-only unless
implementation was requested; follow the caller's output format.

## Preserve existing contracts before assessing the feature

The contract includes existing consumers’ observable behavior, even when the ticket does not repeat it. Before translating the task into feature requirements, identify the shared interfaces and state whose semantics this change alters, then inspect their pre-existing callers and consumers. Treat their supported ordinary behavior as a requirement unless an explicit authorized change replaces it. Feature-local preservation does not establish preservation of a broader shared contract.

For each changed shared state or interface, establish its previous purpose, every distinct relevant entry path and downstream deciding consumer. Compare before/after behavior for a normal ongoing operation, then for the condition that motivated the new mechanism. Carry actual values through arguments, defaults, serialization and predicates. Do not substitute a nearby feature's state, identity test or intended purpose for the state that the consumer actually reads. A source-backed newly broken ordinary path is actionable without the ticket naming that caller. Distinguish this regression from an unrelated pre-existing defect or an invented system-wide guarantee.

## Start with the guarantee

Read the goal, changed interfaces and relevant conventions. Separate an observable
requirement from the author's chosen mechanism or claimed benefit. Record the
source of each decisive requirement. A general convention does not by itself
authorize reversing an explicitly documented scope exception: investigate an
apparent conflict, and leave it unresolved when authority is missing instead of
demanding a larger feature or deployment footprint.

Write the design's load-bearing promise in concrete terms: who may do what, what
state readers may rely on, what survives a crash, or which action is prohibited.
Locate the real authority for that promise: the durable writer, aggregate lock,
control-plane owner or enforcing boundary. Names, comments, configuration intent
and successful happy-path tests are claims to verify, not enforcement.

## Check necessity separately from correctness

Two independent questions must be answered: **does this mechanism need to exist?**
and **does it enforce the promised guarantee?** A working scan, familiar deployment
pattern or justified storage substrate does not settle both. Do not let a concrete
rollout, lock or dispatch defect consume the review while the design premise goes
unchallenged.

For each new operational component, coordination loop or shared lifecycle state,
connect its claimed reason to a requirement and an existing capability. A new
global fence inside an existing helper can widen a feature just as a new service
can. Before accepting periodic
discovery of locally changed state, construct a transition-driven counterfactual:
find the eligibility writer, route a minimal wake-up through the current owner,
reuse current bulk selection, and account for shared active-work gating and
settlement continuation. Test this candidate even when polling is implemented
correctly. Grouping, historical catch-up and handoff recovery are distinct duties;
do not assume all require a permanent normal trigger.

Then state what concrete requirement prevents that alternative, or what tradeoff
remains unresolved. A required collection window, genuinely external observation
or independently unclosed recovery window can justify recurrence. An initial
interval guess, absence of transport delay, or a matching shipped cron pattern
cannot alone prove it necessary. If that necessity remains unestablished, report
the specific source-grounded alternative and open requirement before calling its
infrastructure merge-ready. Conversely, an explicit time-driven requirement or
necessary isolation boundary can justify extra machinery without workload data.

## Choose probes from the changed surface

Select every applicable pass from the changed surface and complete its source
investigation before declaring the approach sound. Several passes can apply.
Do not let a migration error or local cleanup substitute for a guarantee check.

### Shared lifecycle state and invalidation

For changed shared validity, cancellation or reset state, enumerate every writer
and affected consumer, including unchanged handlers and argument defaults. Trace
equivalent updates through direct, synchronized and replayed entry points: does
representation or origin change invalidate work without the semantic identity or
operation changing? Follow adapters and serialization rather than stopping at the
changed caller. Distinct counters may represent different ownership boundaries;
correctness of one does not establish correctness of another.

Construct an ordinary operation still in flight across an identity-preserving
update, then compare actual replacement or termination. Check both rejection of
truly stale work and continuation of legitimate work. Preserve the intended
operation/version fence; explain why a feature needs the shared boundary instead
of its existing local owner.

### Recurring reads and growing work

For any recurring read or refresh, trace one complete cycle through caches,
transport pagination, server predicates and final consumer filtering. State what
bounds rows and requests per cycle. Hold changing work fixed and grow settled
history: does every refresh revisit data that cannot affect the required view?
A page size, documented interval or cache shared among observers does not bound
an exhaustive traversal repeated by the same observer.

Compare a narrower refresh boundary against the same contract. Identify needed
historical and terminal displays, latest-result precedence, settlement updates
and discovery of new work from other actors before recommending a cap or filter.
Preserve those semantics; discarding all completed data or taking only the first
page can create a different correctness bug. Source-derived growth is evidence
of amplification, not a measured production load or an invented performance SLO.

### Reported states, deadlines and completion

Find what a reader does with the state: stop polling, retry, release resources,
bill or advance. Trace the value's writer or derivation and every relevant late
writer. A view, elapsed-time test or missing-output heuristic can change a response
without recording a terminal outcome, cancelling work or fencing later writes.

Try the sequence: a reader observes a supposedly final value, then legitimate
work for the SAME operation/version/attempt commits a contradictory result. Name
what prevents that sequence, or explain why the consumer's decision is unsafe.
An explicit new retry/version is different from late completion of the old one.
Increasing a timeout does not create finality. A repair can enforce durable
terminal outcomes or expose lateness as nonterminal with a truthful stop rule.
Preserve local resource-bounding waits that do not make a false finality promise.

### Transactions, retries and shared aggregates

When SQL source is available, run the bundled read-only context collector first:
`python3 -I <absolute-skill-directory>/scripts/coordination_context.py`
from the supplied case/project directory, with no arguments. Ordinary read-only
file/search commands must remain inside the supplied source or trusted skill.
Do not execute repository code, other scripts, network commands or writes. The
collector provides query/schema/caller
navigation, not a defect verdict or proof of effective constraints. Inspect its
ancestor-deletion evidence and follow the cited files. If execution is unavailable,
perform the same schema walk manually and state any remaining retrieval gap.

Identify the aggregate/root and invariant. Trace the changed transaction, SQL
bodies and commit/rollback. Then retrieve OTHER writers touching the same rows:
completion, reset and deletion, including indirect foreign-key cascades. Search
the table names in query sources AND schema/migrations; competitors need not call
the changed function. A worker claim or duplicate-retry check does not close this
pass.

No direct DELETE of a locked child is not proof that it cannot be deleted. Follow
its owning foreign keys through cascading ancestors, then find those ancestors'
deletion transactions. Verify historical schema evidence has not been superseded.

Write the actual row/key and lock acquisition orders of the changed transaction
and those competitors, including locks taken implicitly by writes, foreign-key
checks and cascades. Test a feasible cycle: A holds one resource and waits for B's,
while B holds that resource and waits for A's. Name the conflicting modes and
reachable operation states. Multiple locks or reversed-looking code alone do
not prove a deadlock. One caller retrying deadlocks does not protect the other;
either can be the victim.

Preserve a consistent aggregate-first protocol when it supplies the invariant.
A nonlocking identifier lookup, owner lock and guarded recheck/update can avoid
child-first acquisition. Preserve authorization, eligibility and atomicity; do
not replace required coordination with a retry or delete it to simplify the graph.

### Security controls, identity and runtime composition

Calculate effective capabilities before and after the change, including independent and inherited allows, denies and scope boundaries. Reapply unchanged grants to moved data and changed consumers. A new conditional grant does not narrow another independent grant. Distinguish object/data reads from writes and administration. Preserve required dependency reads and explicit compatibility; acknowledge any conflict with the promised isolation instead of assuming all stated goals are compatible.


Trace `claimed restriction -> control object -> writer/replacer -> consumer ->
reload/restart lifetime`. Read effective UID/identity, permissions, ownership,
mount modes, startup code and supplied module bodies. Can the constrained actor
rewrite the policy it consumes, replace its parent directory, alter launch code,
or persist such changes for later execution?

Approved or pinned initial bytes do not make a runtime copy immutable. A read-only
file under replaceable writable ancestry is not an immutable control. Trace copying,
rendering, chown/chmod, mounts and restart rather than stopping at the secret,
image or module that supplied the original content.

When a workload can rewrite its own enforced allowlist or persistent launch code,
test the broken defense-in-depth promise even if its initial code was reviewed.
Do not inflate this into unauthenticated access or a new privilege escalation.
Keep enforcement outside that actor's mutation rights, with protected ancestry,
read-only mounts or immutable control rebuilt by its owner; separate writable
data. Writable settings are normal when no restriction depends on them, and
external IAM/database/kernel controls can enforce rights despite mutable app data.

### Async triggers, grouping and recovery

Trace `eligible-state writer -> durable transition -> trigger -> claim/grouping
-> execution -> settlement`. When a scan selects a condition, find who writes it
and what happens immediately afterward. Separate triggering, grouping, coordination,
recovery and finite catch-up instead of assuming one permanent mechanism is needed.

A notification can request scheduling; it need not mean one execution per item.
Inspect whether the existing operation collects all pending work. Coalescing can
use one active execution per entity and a conditional follow-up on settlement;
the active check and insert must be atomic across callers/replicas, and failure,
expiration and duplicate paths also need a continuation owner. This does not
guarantee a fixed collection window; require evidence when that window matters.

Use current owners and transport before assuming another bus, worker or delay
framework is required. A time-driven requirement, external source without push,
or an independently required recovery window can justify recurrence. Historical
backlog alone needs bounded restartable catch-up, not permanent normal polling.

Trace acknowledgement and publication failures. An existing durable task can
return publication errors and replay just the idempotent handoff when redelivery
finds upstream work already completed. Inspect expired and duplicate branches;
do not repeat paid upstream work. Source deduplication alone is not dispatch
recovery: a scan excluding linked rows may miss committed-but-unpublished tasks.
Give the durable handoff a replayable owner or justified recovery. Preserve retry,
dead-letter, integrity and liveness bounds; do not assume an outbox or reconciler
is unavoidable, or promise infinite/exactly-once delivery.

Trace producers and decision-making consumers across available source. Read the
actual functions, SQL and runtime composition, including referenced modules when
supplied. A filename search or opening a nearby handler is not a completed trace.
For shared guarantees, inspect other writers and competing operations, not only
callers of the changed function.

## Try to break the promise

For each triggered pass, construct a short allowed sequence that would falsify
the guarantee: a late completion, concurrent operations, an actor modifying its
own restriction, or a crash during handoff. Tie each step to source and the stated
contract. If the sequence cannot occur, identify the fence, lock, ownership
boundary or protocol that prevents it. Do not dismiss a demonstrated interleaving
as theoretical merely because its production frequency is unknown.

Ask whether the machinery repairs the first broken boundary or compensates
later. Compare one concrete simpler alternative against the same guarantees,
including ordinary failure paths and necessary recovery. Count ongoing
responsibilities and hidden coordination as well as lines of code. A familiar
pattern proves consistency, not necessity; fewer components do not excuse lost
integrity, security, isolation, bounded resources or liveness.

## Validate evidence bounds and operating scope

Starting work before a consumer does not prove completion before that consumer. Trace the actual ordering dependency, complete timeout/cancellation path and retry behavior; a local deadline does not bound an opaque dependency, and an added attempt does not guarantee success. Keep forecasts qualified.

Include explicit trusted operator procedures in allowed counterexamples. A sequence that violates an authorized cutover restriction supports conditional hardening, not failure of that procedure. Trace in-flight automation and uncovered intervals; absence of a machine fence alone does not require one. Do not broaden a scoped one-off or deployment because another environment uses a general convention.

## Derive the verdict and repairs from visible evidence

Put a compact evidence ledger in the caller's existing reason/explanation field; preserve its schema and keep the records concise. Include every material required guarantee, material positive assurance and endorsed repair. A sound verdict endorses the required guarantees even when they are not repeated by name.

For each guarantee use: **claim -> required relation and requirement source -> actual enforcing relation and source -> allowed counterexample and its outcome -> supported scope or exact gap**. Express relations as observable events, states, permissions or bounds. Cite the necessary enforcing edge and the deciding consumer. Mechanism names, nearby code and intended benefits are insufficient. Do not silently turn a hard requirement into best effort; identify the authority for such a change or report the unresolved contract.

For each repair, record its proposed operation and every protected requirement it touches, including explicit exceptions, migration procedures and compatibility. Evaluate both the defect's counterexample and an ordinary protected path under that operation. A repair that fixes one defect by breaking a required contract cannot be endorsed as satisfying the task. State conflicts or conditional scope openly and give a viable fix direction at the responsible boundary; missing evidence does not excuse omitting repair assessment.

Derive positive assurances and repair endorsements from these records. Do not add broader reassurance elsewhere. When an enforcing edge or bound is absent, state what the source actually establishes and the exact remaining gap. Match evidence to the supplied artifact: authoritative design-case facts can support a conditional design assessment; a proposed check is not an executed test or a runtime observation.

Preserve supported defects even when another guarantee is unresolved. A finding still needs the violated promise, source-backed actor/writer path, concrete counterexample and consequence, and viable repair direction. Keep architectural invariants distinct from local implementation issues. Report material supported concerns without forcing a defect for each probe. This ledger is ordinary public technical evidence, not a private reasoning transcript.

## Establish the contract before sharing the draft

Use one fresh checker in two turns with [claim-check.md](references/claim-check.md). Start it before forming the provisional review. Phase one receives the original caller task and canonical requirement-source paths, scoped exceptions, source/diff paths and reference path. It must read those sources directly and completely. Do not provide a provisional review, primary assessment, selected requirement excerpts or findings. The checker first inventories material changed shared boundaries and their pre-existing consumers, alongside task goals. For shared state it evaluates actual writer inputs/defaults/predicates and pending-consumer effects across ordinary validity-preserving versus real invalidating transitions. It returns only a compact `[CONTRACT_MAP]` … `[/CONTRACT_MAP]` recording required outcomes and triggers, authorized scope/exceptions, operational meanings and permitted ordinary behavior, labeled source evidence and open conflicts. No verdict or repairs yet.

Ambiguous language needs an operational interpretation: determine what an observation establishes at that point, with evidence from definitions, consumers and accepted ordinary traces. Interpretation is not automatically a waiver. Distinguish existing versus proposed tests and implementation intent; tests cannot silently override an unambiguous authoritative requirement. A specific authorized exception controls over a generic convention in its scope. Record actual authority conflicts rather than inventing either broader enforcement or a waiver.

On Codex create the checker through native `spawn_agent`, `agent_type="verifier"`, `fork_turns="none"`. After its contract map, make the provisional review and resume THAT SAME checker with it. A coordinator can route the same stages when native leaf delegation is unavailable. On Claude Code create `approach-claim-verifier` through `Agent`, requested `effort="max"`, foreground. After it completes, make the provisional review and use `SendMessage` to its actual returned agent ID. Do not create a second checker or substitute a fresh context. After SendMessage, if the resumed checker is still running, end the current turn with a brief pending-status notice and let the runtime completion notification resume you. This notice is interim, not the final review. Do not start another Agent/fork, poll, or run no-op commands to wait. On headless Claude Code, keep reading the process until its own background run finishes; preliminary parent text is not the final answer. The final-only output rule applies to the completed last response. Native continuation requires session persistence; a host disabling it cannot claim this workflow ran. Do not inspect unrelated session history or infer permissions from an ID.

Phase two receives the provisional final review inside `[PROVISIONAL_REVIEW]` … `[/PROVISIONAL_REVIEW]`. The same checker evaluates obligation applicability before alleging a violation, verifies source claims and compatible repairs against its map, and owns the complete final answer. A material map revision needs cited source evidence and a brief explicit delta; the draft's assertion alone is not evidence. Retain supported findings and viable remedies. Neither a forced error nor loyalty to an incorrect initial interpretation is useful.

The checker uses read/search only: no source execution, source edits, network/history access or delegation. It returns the complete caller-format final review inside `[VERIFIED_REVIEW]` … `[/VERIFIED_REVIEW]`, or writes only explicitly authorized review artifacts. Forward that final payload unchanged, removing only handoff markers. The final answer contains only the requested review: no introduction, closing status, transport explanation, internal draft/map references, post-check conclusions or re-synthesis. Report missing sources or unavailable continuation exactly instead of fabricating a map or a check. Scope, format and user intent remain controlling.
