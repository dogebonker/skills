# Delete Before Adding

Before adding a feature, remove the dead code, flags and branches around it, then add the change to the smaller code.

Refs: https://refactoring.guru/smells/dead-code
Example: [examples/delete-before-adding.py](../examples/delete-before-adding.py)

**Principle** — refactoring.guru's Dead Code smell: variables, parameters, branches and classes left behind when requirements changed. They cost reading time and get carried into each new feature. Beck's fourth rule, fewest elements (https://martinfowler.com/bliki/BeckDesignRules.html), says to remove what does not serve the tests, intention or deduplication. Deleting first shrinks what the new change touches and what reviewers read.

**Violation signals** — Feature flags fixed to one value for months (`LEGACY_CHEQUES_ENABLED = False`). Branches for inputs no caller sends (`fax_order`). Commented-out code. Functions with no callers. A new branch appended next to obsolete ones.

**Fix** — In a separate commit, delete what is dead: the flag, the `cheque` and `fax_order` branches. Then add `gift_card` to the smaller `checkout_fee_cents()`. Prove deadness first: search callers, check logs or metrics for the input, and run the tests. Keep the deletion and the feature in separate commits so each is easy to review and revert.

**When not to apply** — Code reached by external callers, scheduled jobs or rare paths (year-end, disaster recovery) is not dead because local search finds nothing. Removing a public API needs a deprecation period. Deleting changes behaviour for the inputs it drops, so confirm nobody sends them.

**Related** — **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) if payment methods keep growing; [`speculative-generality`](speculative-generality.md); [`yagni`](yagni.md); [`smallest-thing-that-works`](smallest-thing-that-works.md).
