# Answer key for round 2

Point the run at `evals/round2/` only, with `REPO_ROOT` set to the language directory: this file names the dead functions, so a `REPO_ROOT` that contains it turns them live for signal 24. Paths below are relative to `evals/round2/`.

Round 2 plants what round 1 lacks and a real-codebase run missed or mis-ranked. Each language has:
- 5 items to find: 3 kinds of dead code (a cascade, a drifted copy, data read only by dead code), 1 long function that does several jobs, and 1 rule normalized in one place and compared raw in another on the same flow;
- 3 decoys that look like a signal but should be REJECTED: type checks on a vendor payload in a parsing function, one method name in several files that all implement one interface in the scan, and a long function that is a flat table.

Kinds, scoring rules and the simplest-fix rule are those of `evals/expected.md`. Every dead-code row assumes the whole of `evals/round2/<lang>/` was searched, so high confidence is allowed. Line ranges run from the definition line to its last line.

## JavaScript (`javascript/loans.js`, `javascript/notices.js`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| JS2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | loans.js:38-40 (`queueDepth`), loans.js:42-45 (`waitlistPosition`), loans.js:47-49 (`estimatePickupDate`) | JS24: pass 1 for the two callers, pass 2 for `queueDepth` | CONFIRMED, one finding or one per function | delete `waitlistPosition` and `estimatePickupDate`, then `queueDepth`, which only they call |
| JS2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | loans.js:34-36 (`formatDueDate`, unused), notices.js:25-28 (live copy) | JS24 `copy`; JS23 `formatDueDate` in 2 files | CONFIRMED | delete the unused copy in loans.js; the live copy in notices.js keeps its invalid-date guard |
| JS2-A3 | KISS | A | yagni (also accept dead-code) | loans.js:12 (`SEASONAL_LOAN_DAYS`), loans.js:51-53 (`seasonalLoanDays`) | JS24: pass 1 for the function, pass 2 for the table | CONFIRMED | delete the table with its only reader |
| JS2-P1 | SOLID | P | srp (also accept KISS long-function) | loans.js:59-142 (`runDailyCirculation`) | JS25 (85 lines) | CONFIRMED (medium) | Extract Method by reason to change (active loans, overdue and fines, borrowing blocks, notices, renewals, summary text, export rows), so the function reads as a short list of calls; no new classes |
| JS2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | loans.js:55-57 (`isDigital` trims and lowercases), loans.js:83 (raw `loan.format === 'ebook'`) | JS1 at loans.js:83; JS15 `'ebook'` x3 | CONFIRMED (the raw compare fines a `' eBook'` loan that `isDigital` counts as digital) | normalize `format` once (in `parseCatalogRecord` or one helper) and use the same check in both places |
| JS2-D1 | GoF | D | composite, visitor at an I/O boundary | loans.js:25-32 (`parseCatalogRecord`) | JS2, JS11 `[boundary]` | REJECTED: defensive checks on a decoded catalog record | none |
| JS2-D2 | DRY | D | single-source-of-truth, same name in 2 files | notices.js:8-10 (`Notice.render` throws), notices.js:19-22 (`OverdueNotice.render`), loans.js:20-22 (`HoldReadyNotice.render`) | JS23 `render` (override); JS9, JS18 on the base method | REJECTED: overrides of one base method, with bodies that differ by design | none |
| JS2-D3 | SOLID | D | srp, long function | loans.js:144-227 (`languageNames`) | JS25 (85 lines) | REJECTED: a flat lookup table; splitting only moves lines | none |

## TypeScript (`typescript/orders.ts`, `typescript/pricing.ts`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| TS2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | orders.ts:27 (`GROUP_SIZE`), orders.ts:51-53 (`discountTier`), orders.ts:55-57 (`groupDiscountPreview`), orders.ts:59-61 (`bulkRefundQuote`) | TS24: pass 1 for the two exported functions, pass 2 for `discountTier`, pass 3 for `GROUP_SIZE` | CONFIRMED, one finding or one per function | delete the two functions, then `discountTier` and `GROUP_SIZE`, which only they use |
| TS2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | orders.ts:47-49 (`formatTicketPrice`, unused), pricing.ts:23-26 (live copy) | TS24 `copy`; TS23 `formatTicketPrice` in 2 files | CONFIRMED | delete the unused copy in orders.ts; the live copy in pricing.ts keeps its whole-cents guard |
| TS2-A3 | KISS | A | yagni (also accept dead-code) | pricing.ts:13-16 (`EARLY_BIRD_CUTOFFS`), pricing.ts:18-21 (`earlyBirdRate`) | TS24: pass 1 for the function, pass 2 for the table | CONFIRMED | delete the table with its only reader |
| TS2-P1 | SOLID | P | srp (also accept KISS long-function) | orders.ts:67-149 (`settleEventSales`) | TS25 (84 lines) | CONFIRMED (medium) | Extract Method by reason to change (order validation, tickets by tier, gross, fees and refunds, payout split, settlement text, export row); no new classes |
| TS2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | orders.ts:63-65 (`isCash` trims and lowercases), orders.ts:106 (raw `order.paymentMethod === 'cash'`) | TS1 at orders.ts:106 | CONFIRMED (the raw compare charges a card fee on a `' Cash'` order that `isCash` accepts) | normalize `paymentMethod` once, or call `isCash` at orders.ts:106 |
| TS2-D1 | GoF | D | composite, visitor at an I/O boundary | orders.ts:37-45 (`parseWebhookPayload`) | TS2 `[boundary]` | REJECTED: defensive checks on a decoded webhook body | none |
| TS2-D2 | DRY | D | single-source-of-truth, same name in 2 files | pricing.ts:1-3 (`FeeRule.apply`), pricing.ts:8-10 (`PercentFee.apply`), orders.ts:32-34 (`FlatFee.apply`) | TS23 `apply` (override); TS9 `FeeRule: 2` | REJECTED: two implementations of one interface, both used | none |
| TS2-D3 | SOLID | D | srp, long function | orders.ts:151-234 (`currencyNames`) | TS25 (85 lines) | REJECTED: a flat lookup table | none |

## Go (`go/fleet.go`, `go/service/service.go`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| GO2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | fleet.go:70-72 (`garageSlots`), fleet.go:74-80 (`plannedDowntime`), fleet.go:82-88 (`idleCost`) | GO24: pass 1 for the two callers, pass 2 for `garageSlots` | CONFIRMED, one finding or one per function | delete `plannedDowntime` and `idleCost`, then `garageSlots` |
| GO2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | fleet.go:66-68 (`normalizePlate`, unused), service.go:33-39 (live copy) | GO24 `copy`; GO23 `normalizePlate` in 2 files | CONFIRMED | delete the unused copy in package main; the live copy in package service keeps its minimum-length guard |
| GO2-A3 | KISS | A | yagni (also accept dead-code) | fleet.go:20 (`legacyIntervalsKm`), fleet.go:90-95 (`legacyServiceInterval`) | GO24: pass 1 for the function, pass 2 for the map; GO8 package-level var | CONFIRMED | delete the map with its only reader |
| GO2-P1 | SOLID | P | srp (also accept KISS long-function) | fleet.go:101-184 (`planMaintenanceRun`) | GO25 (85 lines) | CONFIRMED (medium) | Extract Method by reason to change (apply pings, find due vehicles, describe fault codes, pick the cheapest workshop, build the report lines); no new types |
| GO2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | fleet.go:97-99 (`isElectric` trims and folds case), fleet.go:129 (raw `v.FuelType == "electric"`) | GO15 `"electric"` x3; no signal hits the raw compare itself | CONFIRMED (the raw compare gives an `"Electric "` van the diesel interval while `isElectric` counts it as electric) | normalize `FuelType` once, or call `isElectric` at fleet.go:129 |
| GO2-D1 | GoF | D | composite, visitor at an I/O boundary | fleet.go:46-64 (`parseTelematicsPayload`) | GO2, GO11 `[boundary]`; GO1 type switch | REJECTED: type switch on decoded JSON | none |
| GO2-D2 | DRY | D | single-source-of-truth, same name in 2 files | fleet.go:33-36 (`Workshop`), fleet.go:40-44 (`depot.Quote`, `depot.WorkOrder`), service.go:21-31 (`Shop.Quote`, `Shop.WorkOrder`) | GO23 `Quote`, `WorkOrder` (override); GO9 `Quote: 2` | REJECTED: two implementations of one interface, both used | none |
| GO2-D3 | SOLID | D | srp, long function | fleet.go:186-269 (`troubleCodes`) | GO25 (85 lines) | REJECTED: a flat lookup table | none |

## Rust (`rust/main.rs`, `rust/payslip.rs`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| RS2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | main.rs:56-58 (`prorate_hours`), main.rs:60-63 (`overtime_forecast`), main.rs:65-67 (`holiday_accrual_preview`) | RS24: pass 1 for the two callers, pass 2 for `prorate_hours` | CONFIRMED, one finding or one per function | delete the two functions, then `prorate_hours` |
| RS2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | main.rs:52-54 (`round_cents`, unused), payslip.rs:20-25 (live copy) | RS24 `copy`; RS23 `round_cents` in 2 files | CONFIRMED | delete the unused copy in main.rs; the live copy in payslip.rs keeps its non-finite guard |
| RS2-A3 | KISS | A | yagni (also accept dead-code) | main.rs:12 (`LEGACY_TAX_BANDS`), main.rs:69-76 (`legacy_tax`) | RS24: pass 1 for the function, pass 2 for the table | CONFIRMED | delete the table with its only reader |
| RS2-P1 | SOLID | P | srp (also accept KISS long-function) | main.rs:82-171 (`run_payroll`) | RS25 (91 lines) | CONFIRMED (medium) | Extract Method by reason to change (hours per badge, gross pay, deductions and net, payslip text, totals); no new types |
| RS2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | main.rs:78-80 (`is_hourly` trims and lowercases), main.rs:112 (raw `e.contract == "hourly"`) | RS15 `"hourly"` x3; no signal hits the raw compare itself | CONFIRMED (the raw compare pays an `"Hourly "` employee as salaried while `is_hourly` counts them as hourly) | parse `contract` once into an enum, or call `is_hourly` at main.rs:112 |
| RS2-D1 | GoF | D | visitor at an I/O boundary | main.rs:41-50 (`parse_clock_payload`) | RS2 `[boundary]` | REJECTED: downcasts on an untyped payload from the clock vendor | none |
| RS2-D2 | DRY | D | single-source-of-truth, same name in 2 files | payslip.rs:1-4 (`Deduction`), payslip.rs:10-18 (`PensionContribution`), main.rs:31-39 (`UnionDues`) | RS23 `amount`, `label` (override); RS9 `Deduction: 2` | REJECTED: two implementations of one trait, both used | none |
| RS2-D3 | SOLID | D | srp, long function | main.rs:173-255 (`country_names`) | RS25 (84 lines) | REJECTED: a flat lookup table | none |

The items are `pub` in a binary crate, which rustc does not report as dead, so the files carry no lint attributes. A `pub` item here is not a published API: the crate has `fn main`.

Not penalised: the `0.21` rate written in `INCOME_TAX_RATE` and in `LEGACY_TAX_BANDS` (main.rs:10, main.rs:12) reported as DRY.

## Kotlin (`kotlin/Schedule.kt`, `kotlin/Billing.kt`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| KT2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | Schedule.kt:35 (`spotsPerHour`), Schedule.kt:37 (`waitlistEta`), Schedule.kt:39-40 (`peakHourShare`) | KT24: pass 1 for the two callers, pass 2 for `spotsPerHour` | CONFIRMED, one finding or one per function | delete `waitlistEta` and `peakHourShare`, then `spotsPerHour` |
| KT2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | Schedule.kt:33 (`formatEuros`, unused), Billing.kt:11-14 (live copy) | KT24 `copy`; KT23 `formatEuros` in 2 files | CONFIRMED | delete the unused copy in package `gym`; the live copy in `gym.billing` keeps its non-negative check |
| KT2-A3 | KISS | A | yagni (also accept dead-code) | Schedule.kt:19 (`LEGACY_DROP_IN_PRICES`), Schedule.kt:42 (`legacyDropInPrice`) | KT24: pass 1 for the function, pass 2 for the map | CONFIRMED | delete the map with its only reader |
| KT2-P1 | SOLID | P | srp (also accept KISS long-function) | Schedule.kt:46-126 (`buildTimetableState`) | KT25 (82 lines) | CONFIRMED (medium) | Extract Method by reason to change (booking validation, waitlists, revenue, exercise plans, timetable rows, weekly counts, occupancy); no new classes |
| KT2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | Schedule.kt:44 (`isVirtual` trims and lowercases), Schedule.kt:75 (raw `gymClass.mode == "virtual"`) | KT15 `"virtual"` x3; no signal hits the raw compare itself | CONFIRMED (the raw compare charges for a `" Virtual"` class that `isVirtual` shows as online) | parse `mode` once into an enum, or call `isVirtual` at Schedule.kt:75 |
| KT2-D1 | GoF | D | composite, visitor at an I/O boundary | Schedule.kt:25-31 (`parsePayload`) | KT2 `[boundary]` | REJECTED: `as?` and `is` checks on a decoded JSON map | none |
| KT2-D2 | DRY | D | single-source-of-truth, same name in 2 files | Billing.kt:3-5 (`PriceRule`), Billing.kt:7-9 (`MemberRate.price`), Schedule.kt:21-23 (`DropInRate.price`) | KT9 `PriceRule: 2`; KT23 lists no `override` functions by design | REJECTED: two implementations of one interface, both used | none |
| KT2-D3 | SOLID | D | srp, long function | Schedule.kt:128-209 (`exerciseNames`) | KT25 (83 lines) | REJECTED: a flat lookup table | none |

## Swift (`swift/Garage.swift`, `swift/Tariffs.swift`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| SW2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | Garage.swift:46-48 (`nightsParked`), Garage.swift:50-52 (`overnightSurcharge`), Garage.swift:54-56 (`monthlyPassBreakEven`) | SW24: pass 1 for the two callers, pass 2 for `nightsParked` | CONFIRMED, one finding or one per function | delete the two functions, then `nightsParked` |
| SW2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | Garage.swift:42-44 (`formatDuration`, unused), Tariffs.swift:15-18 (live copy) | SW24 `copy`; SW23 `formatDuration` in 2 files | CONFIRMED | delete the unused private copy in Garage.swift; the live copy in Tariffs.swift keeps its negative-minutes guard |
| SW2-A3 | KISS | A | yagni (also accept dead-code) | Garage.swift:25 (`legacyHourlyRates`), Garage.swift:58-60 (`legacyRate`) | SW24: pass 1 for the function, pass 2 for the table | CONFIRMED | delete the table with its only reader |
| SW2-P1 | SOLID | P | srp (also accept KISS long-function) | Garage.swift:66-147 (`closeShift`) | SW25 (83 lines) | CONFIRMED (medium) | Extract Method by reason to change (session validation, expected charges, payment reconciliation, regions, report lines, export rows); no new types |
| SW2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | Garage.swift:62-64 (`isMotorcycle` trims and lowercases), Garage.swift:85 (raw `session.vehicleType == "motorcycle"`) | SW15 `"motorcycle"` x3; no signal hits the raw compare itself | CONFIRMED (the raw compare charges a `"Motorcycle"` the car rate while `isMotorcycle` counts it) | parse `vehicleType` once into an enum, or call `isMotorcycle` at Garage.swift:85 |
| SW2-D1 | GoF | D | composite, visitor at an I/O boundary | Garage.swift:33-40 (`parsePayload`) | SW2 `[boundary]` | REJECTED: `as?` casts on a decoded JSON dictionary | none |
| SW2-D2 | DRY | D | single-source-of-truth, same name in 2 files | Tariffs.swift:1-3 (`Tariff`), Tariffs.swift:9-12 (`HourlyTariff.charge`), Garage.swift:27-31 (`EventDayTariff.charge`) | SW23 `charge` (override); SW9 `Tariff: 2` | REJECTED: two conformances to one protocol, both used | none |
| SW2-D3 | SOLID | D | srp, long function | Garage.swift:149-231 (`plateJurisdictions`) | SW25 (84 lines) | REJECTED: a flat lookup table | none |

## Python (`python/meters.py`, `python/tariffs.py`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| PY2-A1 | KISS | A | yagni (also accept dead-code, delete-before-adding) | meters.py:53-55 (`_interpolate`), meters.py:58-59 (`backfill_gaps`), meters.py:62-63 (`smooth_spikes`) | PY24: pass 1 for the two callers, pass 2 for `_interpolate` | CONFIRMED, one finding or one per function | delete `backfill_gaps` and `smooth_spikes`, then `_interpolate` |
| PY2-A2 | KISS | A | yagni (also accept dead-code, DRY single-source-of-truth) | meters.py:49-50 (`round_kwh`, unused), tariffs.py:19-22 (live copy) | PY24 `copy`; PY23 `round_kwh` in 2 files | CONFIRMED | delete the unused copy in meters.py; the live copy in tariffs.py keeps its negative-consumption guard |
| PY2-A3 | KISS | A | yagni (also accept dead-code) | tariffs.py:3 (`LEGACY_BANDS`), tariffs.py:25-30 (`legacy_band_rate`) | PY24: pass 1 for the function, pass 2 for the table | CONFIRMED | delete the table with its only reader |
| PY2-P1 | SOLID | P | srp (also accept KISS long-function) | meters.py:70-152 (`close_billing_cycle`) | PY25 (85 lines) | CONFIRMED (medium) | Extract Method by reason to change (usable reads, consumption per meter, charges and credit, instalments, statement text, export row); no new classes |
| PY2-P2 | DRY | P | single-source-of-truth (also accept duplicated-logic-across-layers) | meters.py:66-67 (`is_estimated` strips and lowercases), meters.py:100 (raw `reading.read_type == "estimated"`) | PY1 at meters.py:100; PY15 `"estimated"` x3 | CONFIRMED (the raw compare holds nothing back for a `" Estimated"` read that `is_estimated` counts) | normalize `read_type` once in `normalize_payload`, or call `is_estimated` at meters.py:100 |
| PY2-D1 | GoF | D | composite, visitor at an I/O boundary | meters.py:39-46 (`normalize_payload`) | PY2 `[boundary]` | REJECTED: `isinstance` checks on a decoded vendor payload | none |
| PY2-D2 | DRY | D | single-source-of-truth, same name in 2 files | tariffs.py:6-8 (`Tariff.charge`), tariffs.py:15-16 (`FlatTariff.charge`), meters.py:35-36 (`DemandTariff.charge`) | PY23 `charge` (override); PY9 `Tariff: 2` | REJECTED: two subclasses of one ABC, both used | none |
| PY2-D3 | SOLID | D | srp, long function | meters.py:155-236 (`country_alpha3`) | PY25 (84 lines) | REJECTED: a flat lookup table | none |

## Totals

| Family | P | A | D | Items to find (P + A) |
|---|---|---|---|---|
| GoF | 0 | 0 | 7 | 0 |
| DRY | 7 | 0 | 7 | 7 |
| KISS | 0 | 21 | 0 | 21 |
| SOLID | 7 | 0 | 7 | 7 |
| All | 14 | 21 | 21 | 35 |
