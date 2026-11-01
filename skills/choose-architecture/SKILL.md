---
name: choose-architecture
description: "Choose the system architecture for a new project or a new service before any code: boundaries, data and consistency, sync vs async, failure handling, service interfaces, LLM components, and the language and framework per service, each decision backed by a cited book rule. Use for 'new project', 'new service' or 'new microservice', 'what architecture should we use', 'monolith or microservices', 'how should we structure this system'. Greenfield only: an existing system enters as fixed contracts."
---

# Choose Architecture

Pick the system-level shape of a new project or a new service. Every choice traces to a stated **force** (a requirement or constraint) and to one rule from the book that owns that kind of decision. Code-level design (patterns, refactoring, class shapes) belongs to `use-patterns` and `architect`, after this skill finishes.

Book rule files live at `~/.agents/skills/<book>/<book>.mini.md`. Load the full `<book>.md` beside it only when the mini rules leave a tradeoff open.

## Decision owners

Each kind of decision has one owning file. The owner decides. A decision that also touches another row's area makes that row's owner advisory for it: when an advisory file disagrees, record both views and the force that settles it.

| Decision kind | Owner |
|---|---|
| Boundaries, and how much modeling each part deserves | `domain-driven-design-distilled` |
| Domain logic shape per part (Transaction Script, Table Module, Domain Model, Service Layer) and data mapping | `patterns-of-enterprise-application-architecture`, applied after the Distilled classification |
| Data: source of truth, stores, consistency, sync vs async, replication, partitioning, events | `designing-data-intensive-applications` |
| Failure and capacity: timeouts, retries, isolation, backpressure, deploy and operations, and how many deployables, stores and queues the team can run | `release-it`, weighed against the Team force |
| Dependency direction inside each deployable, frameworks at the edge | `clean-architecture` |
| Interface depth at each seam between deployables and modules | `a-philosophy-of-software-design`, using the vocabulary in `~/.claude/skills/codebase-design/SKILL.md` (depth, seam, leverage, locality) for the analysis. Client-facing text keeps the client's words, such as "service" and "API" |
| LLM components | [references/ai-systems.md](references/ai-systems.md) |
| Language, runtime, framework and tooling per deployable | [references/stack.md](references/stack.md), house rules |

## Steps

### 1. Scope

Confirm the work is a new project, or a new service joining an existing system. For a new service, list the existing system's contracts it must honour (APIs, events, shared stores, auth) as fixed inputs. This skill takes them as given and leaves the existing system's internals alone.

Done when: the scope is one sentence and every fixed contract is listed, or the user confirms there are none.

### 2. Forces

Forces are the requirements and constraints. Fill each from the brief. Ask the user for every force the brief leaves open, in one batch. A force the user calls unknown becomes a written assumption.

**Functional requirements**: number each user-visible flow FR1, FR2…, one sentence each: who does what, and the outcome. Mark every flow that moves money or takes an irreversible action. Include the read paths users poll (quotes, status, dashboards), since they often outnumber writes.

**Non-functional requirements**: number each NFR1, NFR2… with a unit and a measurement point, such as "order creation p99 under 300 ms at 10 orders/s, measured at the API edge". A target without a number is an open question. Cover:

- **Capability**: what the system does for whom, in the business's own words.
- **Load**: users, average and peak rate per flow (peak factor stated), concurrent long-lived work (open orders, connections, subscriptions), data volume and growth.
- **Consistency**: which data must never be wrong or stale (money, stock, permissions), and which may lag, by how much.
- **Latency and availability**: p99 targets per user-facing path, uptime per path, and recovery targets (RPO, RTO) for each store.
- **Failure cost**: what happens to users and the business when it is down or wrong.
- **Security**: what an attacker gains from each component, and which secrets each one holds.
- **Team**: size, skills, and who runs it in production.
- **Time and money**: deadline and infrastructure budget.
- **Compliance**: regulation, data residency, personal data.
- **LLM use**: what the model does, the quality bar, cost ceiling per request, and which data it may see. Skip when the system has no LLM part.

Then the constraints: Team, Time and money, Compliance.

Done when: every flow has an FR number, every NFR has a number with a unit, and every force has a value from the brief, an answer from the user, or a written assumption.

### 3. Classify

Read the `domain-driven-design-distilled` mini file. Split the capability into subdomains and label each Core, Supporting or Generic, judged against the whole business: for a new service inside a larger system, a part is Core only when it is what sets the business apart. Generic parts get bought or kept simple. Core parts get the modeling effort, and so does any Supporting part holding data the Consistency force marks as never wrong.

Done when: every part of the capability has one label and a one-line reason tied to a force.

### 4. Outside systems

List every third-party system, protocol and regulation the brief names: payment providers, brokers, help desks, SaaS APIs, file formats, data-protection and sector rules. For each, note the gotchas the design must respect: delivery and acknowledgement semantics, idempotency windows, rate limits, timing limits, formats it already provides that remove work, and regulatory must-haves. Confirm each behavior the design will rest on against the system's official docs. A behavior you could not confirm goes into the output marked "unverified".

Done when: every named outside system has its gotchas listed and each behavior is either confirmed with a doc link or marked unverified.

### 5. Capacity

Turn the Load NFRs into peak rates per component: requests per second per endpoint, database writes per second, outbound calls per second per outside system, concurrent long-lived work, and CPU time per request. Put each rate next to its limit: provider rate limits and quotas from step 4, one database primary, one event-loop core, one wallet's transaction ordering. The tightest ratio is the bottleneck. Language, runtime and deployable-count choices quote this arithmetic.

Done when: every Load NFR is a peak rate per component, each rate has its limit beside it, and the bottleneck is named.

### 6. Candidates

Design it twice: sketch at least two candidates that differ in whole shape, such as one deployable vs several, request/response vs events, one store vs several. Include the simplest candidate that meets the forces. For a new project the default candidate is a modular monolith: one deployable whose modules follow the step 3 subdomains, each module owning its own tables and exposing one interface, with module seams checked in CI so any module can later move out as its own service. A candidate with several deployables names the force one deployable cannot meet: independent scaling, a separate owning team, failure isolation, or a different runtime. When nothing is Core, or Generic parts make up most of the capability, one candidate buys or reuses an existing product for those parts. When the brief fixes a shape that rules out the simplest candidate, keep that candidate, recommend the shape the brief asked for, and state the condition under which the simpler one wins. Each candidate states its deployables, boundaries, data ownership (one writer per piece of data), communication, failure handling, and LLM components. An outside system a candidate adds gets the step 4 check.

Done when: two or more candidates differ on at least one whole-shape axis and each covers all six items.

### 7. Screen

Check every candidate against [references/red-flags.md](references/red-flags.md). Then compare interface depth per the `a-philosophy-of-software-design` mini file: a seam that hides much behind a small interface counts for the candidate; a shallow one (pass-through, chatty, callers must know sequencing or internals) counts against it.

Done when: every candidate has its red-flag hits listed and each seam is rated deep or shallow with a reason.

### 8. Decide

List the decision kinds in play, then read each owner's mini file before deciding that kind. Read advisory files only where a candidate touches their area. For each decision record:

- the options considered
- the choice
- the force that decided it
- the one owner rule that decided it, quoted
- any advisory disagreement, and the force that settles it
- **revisit when**: the observable change in a force that would reopen the decision

Done when: every decision kind in play has a record, and every choice names a force and quotes a rule.

### 9. Deliver

Ask the user which format they want: a chat summary, ADRs (one per significant decision in `docs/adr/` plus a one-page overview linking them), or an HTML page via `archify`. Write that format. Lead with the recommendation and the open questions. Put the capacity arithmetic in the main text when it decides the stack or the deployable count. Keep the main text around 1,200 words for a chat summary. The appendix or ADR files hold only what the main text leaves out: the forces table, the red-flag screen, seam ratings, and the record fields the main text skips. Each decision, candidate and question appears once.

Done when: the chosen format exists and contains every record from step 8, the classification, the rejected candidates with why they lost, and the step 4 gotchas, the main text reads on its own without the appendix, and nothing in the appendix restates the main text.
