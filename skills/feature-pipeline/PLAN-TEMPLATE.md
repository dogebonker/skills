# Delivery Plan Template

The architect emits the Phase 2 delivery plan in this exact shape. Keep phases ordered by
dependency; each phase is one reviewable, committable, green-on-its-own vertical slice.
Drop sections that don't apply — don't pad. Use the [LANGUAGE.md](../improve-codebase-architecture/LANGUAGE.md)
vocabulary (Module, Interface, Depth, Seam, Adapter) when describing structure.

---

# <Feature name> — delivery plan

**Brief:** <1–3 sentences: what we're building and why, in the domain's own terms (from CONTEXT.md).>

**Architecture summary:** <The chosen shape in 3–6 bullets. For each module: its interface, why
it's deep (large behaviour behind a small interface), and the deletion-test justification. Call
out where SOLID / smell-removal was applied *and where it was deliberately skipped* to stay simple.>

**Module map:**

| Module | Interface (what a caller must know) | Depth note | New / changed |
| --- | --- | --- | --- |
| `<name>` | `<the small surface>` | deep: hides `<what>` | new |

**Residual risks / open questions:** <anything the critic flagged that we're accepting, or
decisions deferred to a later phase.>

---

## Phases

> One phase = one commit. Size so the diff reads in one sitting. Each phase leaves tests green.

### Phase 1 — <short imperative title>

- **Goal:** <the one capability this phase delivers; a user/caller-visible outcome where possible.>
- **Depends on:** <none | Phase N> 
- **Touches:** <files / modules created or changed — be specific, e.g. `src/money/parse.go`.>
- **Tests (the spec):** <the behaviours that prove this phase, by public interface — written first
  in Phase 3 and red until this phase is implemented. e.g. "parses `1 234,50` → 123450 minor units".>
- **Notes:** <implementation hints, the seam being introduced, anything non-obvious. Keep it the
  smallest viable diff — no abstractions for single-use logic.>
- **Verify:** <command(s) to run, e.g. `go test ./money/...`> green + `lsp_diagnostics` clean.
- **Commit:** `feat: <conventional subject for this phase>`

### Phase 2 — <short imperative title>

- **Goal:** …
- **Depends on:** Phase 1
- **Touches:** …
- **Tests (the spec):** …
- **Notes:** …
- **Verify:** … green + lsp clean.
- **Commit:** `feat: …`

<…repeat per phase…>

---

## Definition of done

- [ ] Every phase committed (one focused commit each), tree green after each.
- [ ] Full suite + build pass on fresh output.
- [ ] Independent `verifier`/`critic` check against this plan and the Phase 1 brief.
- [ ] Docs landed: `CONTEXT.md` terms, any `docs/adr/NNNN-*.md`, this plan doc.

---

### Worked micro-example (delete in real plans)

> **Phase 1 — Parse Ukrainian money strings**
> - **Goal:** turn user-typed amounts like `1 234,50 грн` into integer minor units.
> - **Depends on:** none
> - **Touches:** `src/money/parse.go`, `src/money/parse_test.go`
> - **Tests (the spec):** `1 234,50` → 123450; bare `50` → 5000; rejects `12,3,4`.
> - **Notes:** one deep `ParseMoney(string) (Amount, error)` — the seam is the `Amount` type,
>   not the parser internals. No separate tokenizer module (deletion test: nothing reappears).
> - **Verify:** `go test ./money/...` green + lsp clean.
> - **Commit:** `feat: parse Ukrainian money strings to minor units`
