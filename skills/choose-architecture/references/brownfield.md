# Brownfield changes

For a change to the system-level shape of something that already runs: splitting a monolith, extracting a service, merging services, replacing a store or a queue, moving platform. Module-level refactoring inside one deployable belongs to `improve-codebase-architecture` and `use-patterns`.

The existing system is evidence, not a brief. Every claim about it comes from code, config, deploy files, metrics or git history. A diagram or doc is a claim to check against them.

## B1. As-is map (before step 2)

From the code and deploy config, list every deployable, store, queue and outside system. For each piece of data, name the deployable that writes it, citing `file:line`. List the calls between deployables, sync or async. Take load, latency and error rates from metrics or logs where they exist, and label every other number "inferred".

Done when: every deployable and store is listed, every writer is cited from code, and every number is either measured or labelled inferred.

## B2. Pain (before step 2)

Name the problems that motivate the change, P1, P2…, each with evidence and a measure:
- incidents and their causes
- lead time for a change
- change hotspots: files in different modules that git history shows changing together
- a scaling limit that has been hit
- cost

A pain with no evidence is a claim and stays one. When no pain has evidence, the recommendation is to keep the current shape.

Done when: every pain has evidence and a measure, or is marked as a claim.

## Changes to the main steps

- **Step 2 Forces** gains **Change cost**: how much of the running system each candidate touches, the test coverage on those paths, and how long the team can tolerate a feature freeze. Load and latency forces start from the B1 measurements.
- **Step 3 Classify** maps the subdomains onto today's code, so the Core part of the business is located in files.
- **Step 5 Capacity** uses measured rates from B1 wherever they exist.
- **Step 6 Candidates**: the simplest candidate keeps the current shape and fixes each pain locally. Every other candidate is a target shape plus a path to it, and names the pains it removes.

## B3. Migration path (after step 8)

For the chosen target, list the steps in order. Each step:
- ships on its own and leaves the system working
- has a rollback
- has a done signal you can observe
- adds characterization tests at the seam it moves, before moving it (`working-effectively-with-legacy-code`)

Choose the move per step:
- **Strangler fig**: route one flow at a time to the new part, behind a switch.
- **Branch by abstraction**: put an interface in front of the old part, build the new one behind it, then flip.
- **Parallel run**: send live traffic to both and compare outputs before the new part's results count.
- **Expand and contract** for schemas: add the new shape, migrate readers and writers, then remove the old one.
- **Change data capture or backfill** when data moves between stores. Application code never writes both stores (`designing-data-intensive-applications`).

Order the steps so the first one removes a measured pain. Every period with two live paths has an end date.

Done when: every step has a rollback, a done signal and its characterization tests, the first step removes a pain from B2, and each period with two live paths has an end date.

## Delivery

The step 9 output adds the as-is map, the pains with their evidence, and the migration path. The main text leads with the first migration step, alongside the recommendation.
