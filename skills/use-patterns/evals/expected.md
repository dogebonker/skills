# Answer key for the fixtures

Point the run at `evals/fixtures/` only; this file sits outside that path. Paths below are relative to `evals/fixtures/`.

Each language has:
- 7 opportunities and violations to find: 4 GoF, 1 DRY, 1 SOLID, and 1 KISS that is not pattern overuse;
- 1 pattern-overuse case (KISS);
- 5 decoys that look like a signal but should be REJECTED: 2 GoF-shaped, 1 DRY, 1 SOLID, 1 KISS.

Kinds: P is a finding whose fix adds or reshapes structure, A is one whose fix removes structure, D is a decoy.

Scoring a run:
- **Recall**: a P or A item counts as found when the report names its location (any listed line), its family, the expected id or pattern, and a fix in the expected direction. Count a finding that merges the listed locations into one entry as one hit, which is the expected shape. A listed "also accept" family or id scores the same.
- **Verdict**: P and A items are expected CONFIRMED unless the row says otherwise. A WEAK verdict with the right fix scores half.
- **False positive**: a D item reported as a P or A finding, or a P or A finding that matches no row here and no "Not penalised" note. A D item listed under "Considered and rejected" is correct. A low-confidence WEAK note on a D item scores neither way.
- **Simplest fix**: where the row names an idiom, a full class-based pattern without saying why the idiom falls short counts as a wrong fix. An interface added with one implementation and no test double counts as a wrong fix.

Hits from the scan that sit inside an item (for example the `.status =` assignments inside a State item) belong to that item and are not separate findings.

## JavaScript (`javascript/checkout.js`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| JS-P1 | GoF | P | strategy (also accept SOLID ocp) | checkout.js:56 (`shippingCost`), checkout.js:71 (`deliveryDays`) | switch on `order.shippingMethod`, 4 variants, same switch in 2 functions | CONFIRMED, one finding with both locations | idiom: one object per method in a lookup (`{ standard: { cost, days }, ... }`) replacing both switches; no class hierarchy |
| JS-P2 | GoF | P | observer | checkout.js:113-115 (`pay`), checkout.js:123-125 (`cancel`) | hard-coded calls to mailer, inventory, analytics after each status change | CONFIRMED (medium) | idiom: `EventEmitter` (or a listener list) with `order_paid` / `order_cancelled`; register the three dependents at the composition root |
| JS-P3 | GoF | P | builder | checkout.js:26 (constructor, 9 params), calls checkout.js:141-142 | long positional list with `false, null, null, null` placeholders | CONFIRMED | idiom: options object with defaults; a full Builder is not needed |
| JS-P4 | GoF | P | null-object | checkout.js:81, checkout.js:86, checkout.js:91 | `customer.loyalty` checked at 3 sites with neutral defaults | CONFIRMED | a frozen default loyalty object assigned when a customer has none; delete the three checks |
| JS-P5 | DRY | P | single-source-of-truth | checkout.js:156 (`validateAddress`), checkout.js:160-167 (`countryOptions`) | the shipping country list written twice | CONFIRMED | one `SHIPPING_COUNTRIES` declaration (code and label); the validator and the options both derive from it |
| JS-P6 | SOLID | P | dip | checkout.js:196 (`new PaymentsHttpClient` in `RefundService`), checkout.js:200 (`new Date()`) | business service builds its HTTP client from `process.env` and reads the clock | CONFIRMED | pass the payments client (and a `now` function) into `RefundService`'s constructor; build them in the composition root; no interface needed |
| JS-P7 | KISS | P | flat-over-nested | checkout.js:173-187 (`refundAmount`) | 4 nested `if` levels, result variable returned at the end | CONFIRMED | guard clauses returning 0 for cancelled, unpaid and out-of-window orders; normal path last |
| JS-A1 | KISS | A | speculative-generality (needless indirection) | checkout.js:10-23 (`OrderRepository`) | every method forwards unchanged to `this.db` | CONFIRMED | Remove Middle Man: pass the `MemoryDb` to `CheckoutService` and delete `OrderRepository` |
| JS-D1 | GoF | D | value lookup | checkout.js:40-47 (`currencyFor`) | switch on country | REJECTED: returns constants, 3 cases plus a default (also below the data-over-code bar) | none |
| JS-D2 | GoF | D | flag, 2 cases | checkout.js:49-52 (`formatPrice(..., compact)`) | boolean parameter | REJECTED: two stable cases | none |
| JS-D3 | DRY | D | knowledge-not-text | checkout.js:150-151 (`SKU_PATTERN`, `VOUCHER_PATTERN`) | the same regex twice | REJECTED: equal by coincidence, SKU and voucher formats change for different reasons | none |
| JS-D4 | SOLID | D | srp | checkout.js:205-218 (`Money`) | class with many methods | REJECTED: cohesive value type, every method works on the same amount and currency | none |
| JS-D5 | KISS | D | speculative-generality | checkout.js:220-227 (`importItems(rows, onProgress)`) | hook-shaped parameter | REJECTED: the demo caller passes `onProgress` (checkout.js:230) | none |

Not penalised: the literal `'US'` checks in `deliveryDays` (checkout.js:72-73) reported inside JS-P1 or JS-P5.

## TypeScript (`typescript/billing.ts`, `typescript/documents.ts`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| TS-P1 | GoF | P | state (also accept SOLID ocp) | billing.ts:10 (`paymentSucceeded`), billing.ts:25 (`paymentFailed`) | `switch (this.status)` in 2 methods, transitions, 4 states | CONFIRMED | idiom: one transition function over the `SubscriptionStatus` union (or a table keyed by state and event) with a `never` check |
| TS-P2 | GoF | P | adapter | billing.ts:64, billing.ts:74, billing.ts:80 | 3 call sites convert euros to `amount_cents`, use snake_case vendor fields and check `status_code` | CONFIRMED | one adapter over `AcmePayClient` in euros that turns status codes into errors; no interface unless a second provider is expected |
| TS-P3 | GoF | P | visitor | documents.ts:8 (`wordCount`), documents.ts:19 (`toHtml`), documents.ts:29 (`toPlainText`) | `instanceof` chains over the same 4 block classes in 3 operations | CONFIRMED, one finding | idiom: discriminated union with a `kind` tag and an exhaustive `switch` with a `never` check |
| TS-P4 | GoF | P | decorator | documents.ts:46-68 (`ReportFetcher`, flags at documents.ts:50) | `useCache`, `retries`, `logRequests` toggle extras around one call | CONFIRMED | idiom: higher-order wrappers `withCache(withRetry(withLogging(fetchText)))`; delete the flags |
| TS-P5 | DRY | P | magic-values | billing.ts:84, billing.ts:88 (`1209600000`), billing.ts:92 (`259200`) | raw millisecond and second durations, one repeated | CONFIRMED | named durations built from units (`TRIAL_LENGTH_MS = 14 * DAY_MS`, `RETRY_INTERVAL_S = 3 * DAY_S`) |
| TS-P6 | SOLID | P | lsp | documents.ts:76-79 (`PdfExporter.append` throws), documents.ts:82 (`instanceof PdfExporter` guard) | override refuses the parent's operation; caller type-checks | CONFIRMED | split the capability: `append` only on exporters that support it (or drop the inheritance); delete the `instanceof` guard |
| TS-A2 | KISS | A | speculative-generality | documents.ts:86-94 (`RenderOptions`, `renderReport(options, beforeRender)`) | option bag and hook never read, no caller passes them | CONFIRMED | delete `RenderOptions`, `options` and `beforeRender`; `renderReport(blocks)` |
| TS-A1 | KISS | A | pattern-overuse | billing.ts:50-55 (`InvoiceNumberGenerator`) | interface with one implementation, no test double | CONFIRMED | use the class (or a counter function) directly and delete the interface |
| TS-D1 | GoF | D | value lookup | billing.ts:41-48 (`statusLabel`) | switch on status | REJECTED: maps state to a label; may be noted inside TS-P1 | none |
| TS-D2 | GoF | D | the one factory | documents.ts:39-44 (`exporterFor`) | switch on format | REJECTED: the single place that picks the exporter, 2 cases | none |
| TS-D3 | DRY | D | knowledge-not-text | billing.ts:95-96 (`MAX_SEATS_PER_PLAN`, `INVOICE_DUE_DAYS`, both 30) | repeated literal | REJECTED: named, equal by coincidence | none |
| TS-D4 | SOLID | D | srp | documents.ts:98-109 (`DateRange`) | class with many methods | REJECTED: cohesive value type | none |
| TS-D5 | KISS | D | pattern-overuse | billing.ts:98-112 (`Notifier`, `EmailNotifier`, `SmsNotifier`, `notifierFor`) | interface plus factory | REJECTED: two real implementations chosen by customer preference | none |

## Go (`go/warehouse.go`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| GO-P1 | GoF | P | composite | warehouse.go:17-21 (`Box.Contents []any`), warehouse.go:24 (type switch in `totalWeight`) | tree held as `[]any`, walked with a type switch | CONFIRMED (medium; WEAK accepted, one operation) | interface `Item { Weight() float64 }` on `Product` and `Box`; `Contents []Item` |
| GO-P2 | GoF | P | command (also accept SOLID ocp) | warehouse.go:56 (`switch parts[0]` in `Execute`) | dispatcher on a command word, 4 actions, history of raw strings | CONFIRMED (medium) | idiom: `map[string]func(...)` with lookup and an unknown-operation error; no command objects (no undo) |
| GO-P3 | GoF | P | template-method | warehouse.go:111 (`exportCSV`), warehouse.go:120 (`exportMarkdown`), warehouse.go:129 (`exportHTML`) | 3 functions with the same steps | CONFIRMED | one `export(w, products, f format)` taking a struct of funcs or a small interface |
| GO-P4 | GoF | P | builder | warehouse.go:94 (`NewShipment`, 8 params, 3 bools), calls warehouse.go:145-146 | placeholders `false, false, false, ""` | CONFIRMED | idiom: an options struct literal or functional options |
| GO-P5 | DRY | P | duplicated-logic-across-layers | warehouse.go:154 (`parseReceiveForm`), warehouse.go:165 (`saveStock`) | the SKU rule (6 chars, `SK` prefix) written in the request layer and the storage layer with different messages | CONFIRMED | one `validSKU(sku) error` both layers call; the storage check stays as the boundary |
| GO-P6 | SOLID | P | srp (also accept dip) | warehouse.go:172-190 (`writeDailyReport`) | stock valuation, text layout and file writing in one function | CONFIRMED | split into `stockValue(products, stock)`, `renderReport(...)` and a thin writer that takes an `io.Writer` |
| GO-A2 | KISS | A | premature-optimization | warehouse.go:192-201 (`weightCache`, `cachedWeight`) | global cache keyed by label, no invalidation, around a cheap walk | CONFIRMED | delete the cache and call `totalWeight` directly |
| GO-A1 | KISS | A | pattern-overuse | warehouse.go:37-45 (`StockStore`, only `memoryStore`) | interface with one implementation, no test double | CONFIRMED | hold `*memoryStore` directly; keep only if a test double is added |
| GO-D1 | GoF | D | value lookup | warehouse.go:76-86 (`unitFactor`) | switch on unit | REJECTED: returns constants | none |
| GO-D2 | GoF | D | 2-case type switch | warehouse.go:102-109 (`httpStatus`) | type switch on error | REJECTED: two stable cases | none |
| GO-D3 | DRY | D | knowledge-not-text | warehouse.go:203-204 (`linesPerPickList`, `lowStockThreshold`, both 40) | repeated literal | REJECTED: named, equal by coincidence | none |
| GO-D4 | SOLID | D | srp | warehouse.go:206-214 (`Dimensions` and its 7 methods) | type with many methods | REJECTED: cohesive value type | none |
| GO-D5 | KISS | D | pattern-overuse | warehouse.go:216-234 (`Notifier`, `emailNotifier`, `slackNotifier`, `alertLowStock`) | interface | REJECTED: two real implementations, both used | none |

Note: `StockStore` (GO-A1) stays a one-implementation interface even though `alertLowStock` takes it; `Notifier` (GO-D5) is the justified one.

## Rust (`rust/invoicing.rs`, `rust/messaging.rs`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| RS-P1 | GoF | P | null-object | invoicing.rs:21, invoicing.rs:28, invoicing.rs:35 | `Option<Box<dyn DiscountPolicy>>` matched at 3 sites with neutral defaults | CONFIRMED | a `NoDiscount` implementation; field becomes `Box<dyn DiscountPolicy>`. Option combinators alone score half |
| RS-P2 | GoF | P | builder | invoicing.rs:45 (`Invoice::new`, 7 params), calls invoicing.rs:72-73 | `None, None, false` placeholders | CONFIRMED | idiom: builder methods taking `self`, or `Default` with struct update syntax |
| RS-P3 | GoF | P | factory-method | messaging.rs:22, messaging.rs:32 | the same `match c.channel.as_str()` constructing 3 senders in 2 functions | CONFIRMED | one `fn sender_for(channel) -> Box<dyn Sender>`, or parse into an enum with a `sender()` method |
| RS-P4 | GoF | P | observer | messaging.rs:51-62 (`post_payment`, `post_refund`) | each posting calls audit, dashboard and outbox by hand | CONFIRMED (medium) | subscribers `Vec<Box<dyn FnMut(&LedgerEvent)>>`; `post_*` publish one event |
| RS-P5 | DRY | P | single-source-of-truth | invoicing.rs:76 (`rate: 0.23`), invoicing.rs:97 (`0.23` and `"23%"`), invoicing.rs:98 (`1.23`) | the VAT rate written in three forms | CONFIRMED | one `VAT_RATE` constant; the label and the gross factor derive from it |
| RS-P6 | SOLID | P | isp (also accept lsp) | invoicing.rs:122-128 (`InvoiceStore`, 5 methods), invoicing.rs:145, invoicing.rs:147 (`unimplemented!` in `ArchiveStore`), invoicing.rs:152 (`archive_all` uses `put` only) | fat trait with stubbed methods | CONFIRMED | split into small traits; `archive_all` takes the one it uses; `ArchiveStore` implements only what it supports |
| RS-P7 | KISS | P | flat-over-nested | invoicing.rs:100-120 (`reminder_text`) | 4 nested levels returning `None` from several branches | CONFIRMED | guards returning `None` early, then the two messages |
| RS-A1 | KISS | A | pattern-overuse | invoicing.rs:62-68 (`TaxRule`, only `VatRule`) | trait with one `impl`, used once | CONFIRMED | take `&VatRule` (or the rate) in `gross` and delete the trait |
| RS-D1 | GoF | D | value lookup | invoicing.rs:51-58 (`symbol`) | `match` on currency | REJECTED: returns constants | none |
| RS-D2 | GoF | D | flag, 2 cases | invoicing.rs:60 (`late_fee(..., business)`) | bool parameter | REJECTED: two stable cases | none |
| RS-D3 | DRY | D | knowledge-not-text | invoicing.rs:94-95 (`PAYMENT_TERMS_DAYS`, `MAX_LINES_PER_INVOICE`, both 30) | repeated literal | REJECTED: named, equal by coincidence | none |
| RS-D4 | SOLID | D | srp | invoicing.rs:158-170 (`Cents` and its 8 methods) | type with many methods | REJECTED: cohesive value type | none |
| RS-D5 | KISS | D | pattern-overuse | invoicing.rs:1-16 (`DiscountPolicy`, `Percentage`, `FixedAmount`) | trait | REJECTED: two real implementations | none |

Not penalised: the `30` due days in `Invoice::new("INV-1", "EUR", 30, ...)` (invoicing.rs:72) reported as a magic value.

## Kotlin (`kotlin/Booking.kt`, `kotlin/FrontDesk.kt`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| KT-P1 | GoF | P | state (also accept SOLID ocp) | Booking.kt:21 (`confirm`), Booking.kt:29 (`checkIn`), Booking.kt:37 (`checkOut`), Booking.kt:42 (`cancel`), Booking.kt:49 (`refundable`) | `when (status)` in 4 methods, transitions, 5 states | CONFIRMED | idiom: sealed states with an exhaustive `when`, or one transition function keyed by (status, event) |
| KT-P2 | GoF | P | command | FrontDesk.kt:22 (`handle`), FrontDesk.kt:40 (`undoLast`) | `when (parts[0])` on 4 request names, switched again for undo | CONFIRMED | sealed interface `Request` with `execute()` and `undo()` (or a map of name to execute/undo lambdas) |
| KT-P3 | GoF | P | template-method | FrontDesk.kt:54 (`PdfInvoice`), FrontDesk.kt:64 (`EmailInvoice`), FrontDesk.kt:74 (`SmsInvoice`) | 3 classes with the same `render` steps | CONFIRMED | idiom: one `render(folio, format)` taking lambdas or a small format object |
| KT-P4 | GoF | P | adapter | FrontDesk.kt:13, FrontDesk.kt:14, FrontDesk.kt:15 | `fx.quote("EUR$currency").toDouble()` at 3 call sites | CONFIRMED | idiom: extension `fun LegacyFxService.rate(from, to): Double` |
| KT-P5 | DRY | P | magic-values | Booking.kt:58, Booking.kt:60 (`48`), Booking.kt:62 (`172800`) | the free-cancellation window as raw hours twice and as raw seconds once | CONFIRMED | `FREE_CANCELLATION_HOURS = 48`; the reminder delay derived as `FREE_CANCELLATION_HOURS * 3600L` |
| KT-P6 | SOLID | P | lsp | Booking.kt:72-74 (`StaffRoom.upgradeTo` throws), Booking.kt:76 (`is StaffRoom` guard) | override refuses the parent's operation; caller type-checks | CONFIRMED | move `upgradeTo` to the room types that support it (an `Upgradable` interface, or composition); delete the `is` guard |
| KT-A2 | KISS | A | speculative-generality | Booking.kt:78-79 (`occupancyReport(format, locale, onLine)`) | three parameters never read and never passed (kotlinc warns) | CONFIRMED | remove the three parameters |
| KT-A1 | KISS | A | pattern-overuse (also accept SOLID dip) | Booking.kt:6 (`object TaxSettings` with `var`), read at Booking.kt:54 | mutable global read inside `total()` | CONFIRMED | pass `cityTaxPerNight` into `Booking`; delete `TaxSettings` |
| KT-D1 | GoF | D | value lookup | Booking.kt:8-12 (`capacity`) | `when` on room type | REJECTED: returns constants | none |
| KT-D2 | GoF | D | flag, 2 cases | Booking.kt:14 (`nightlyPrice(..., weekend)`) | Boolean parameter | REJECTED: two stable cases | none |
| KT-D3 | DRY | D | knowledge-not-text | Booking.kt:64-65 (`MAX_GUESTS_PER_BOOKING`, `LOYALTY_POINTS_PER_NIGHT`, both 8) | repeated literal | REJECTED: named, equal by coincidence | none |
| KT-D4 | SOLID | D | srp | Booking.kt:81-90 (`DateSpan`) | class with many methods | REJECTED: cohesive value type | none |
| KT-D5 | KISS | D | pattern-overuse | FrontDesk.kt:98-108 (`Notifier`, `EmailNotifier`, `SmsNotifier`) | interface | REJECTED: two real implementations, both used | none |

Not penalised: the default checkout hour `11` written at FrontDesk.kt:11 and FrontDesk.kt:43 reported as a DRY magic value, together with KT-P5 or on its own.

## Swift (`swift/Delivery.swift`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| SW-P1 | GoF | P | strategy (also accept SOLID ocp) | Delivery.swift:41 (`deliveryFee`), Delivery.swift:51 (`feeExplanation`) | `switch d.feeMode` on a string, 4 variants, in 2 functions | CONFIRMED, one finding | idiom: `enum FeeMode` with computed `fee(for:)` and `explanation` via exhaustive `switch` |
| SW-P2 | GoF | P | composite | Delivery.swift:7-11 (`Combo.parts: [Any]`), Delivery.swift:13-23 (`price`, `names` with `as?`) | tree as `[Any]`, 2 walks with type casts | CONFIRMED | protocol `MenuNode` adopted by `Dish` and `Combo`; `parts: [any MenuNode]` (an `indirect enum` is acceptable) |
| SW-P3 | GoF | P | decorator | Delivery.swift:60-72 (`PriceCalculator` flags), Delivery.swift:119 | 3 Bool flags adding ordered extras around a subtotal | CONFIRMED (medium) | idiom: an ordered array of `(Double) -> Double` adjustments |
| SW-P4 | GoF | P | observer | Delivery.swift:106-112 (`didSet` on `status`) | setter calls 3 dependents by hand | CONFIRMED (medium) | a list of `(String) -> Void` observers (or Observation/Combine) |
| SW-P5 | DRY | P | single-source-of-truth | Delivery.swift:127, Delivery.swift:129, Delivery.swift:131 | the 8 km delivery radius written three times (`8`, `8`, `8.0`) | CONFIRMED | one `deliveryRadiusKm` constant used by all three |
| SW-P6 | SOLID | P | isp (also accept lsp) | Delivery.swift:136-142 (`MenuStore`, 5 requirements), Delivery.swift:162-164 (`fatalError` stubs in `PublishedMenu`), Delivery.swift:168 (`cheapestDish` uses `dishes()` only) | fat protocol with stubbed requirements | CONFIRMED | split into a reading protocol and an editing protocol; `PublishedMenu` conforms only to reading; `cheapestDish` takes the reading one |
| SW-A2 | KISS | A | premature-optimization | Delivery.swift:170-179 (`FeeCache`) | cache around cheap arithmetic, key ignores `basketTotal` and truncates `km` | CONFIRMED | delete `FeeCache`; call `deliveryFee` |
| SW-A1 | KISS | A | pattern-overuse | Delivery.swift:92-96 (`OrderFactory.makeOrder`) | static factory whose body is the initializer | CONFIRMED | call `Order(id:items:)` directly |
| SW-D1 | GoF | D | value lookup | Delivery.swift:25-32 (`prepMinutes`) | switch on category | REJECTED: returns constants | none |
| SW-D2 | GoF | D | the one factory | Delivery.swift:80-85 (`makeCourier`) | switch on vehicle | REJECTED: the single place that creates couriers | none |
| SW-D3 | DRY | D | knowledge-not-text | Delivery.swift:133-134 (`maxDishesPerCombo`, `courierShiftHours`, both 6) | repeated literal | REJECTED: named, equal by coincidence | none |
| SW-D4 | SOLID | D | srp | Delivery.swift:181-191 (`Basket`) | type with many members | REJECTED: cohesive value type | none |
| SW-D5 | KISS | D | pattern-overuse | Delivery.swift:74-76 (`Courier`, `BikeCourier`, `CarCourier`) | protocol | REJECTED: two real conformers chosen by vehicle | none |

Not penalised: the free-delivery threshold `25` repeated at Delivery.swift:44 and Delivery.swift:54 reported as DRY, inside SW-P1 or on its own.

## Python (`python/policies.py`, `python/claims.py`)

| ID | Family | Kind | Id | Where | Signal | Expected verdict | Expected fix |
|---|---|---|---|---|---|---|---|
| PY-P1 | GoF | P | visitor | policies.py:25 (`premium`), policies.py:35 (`describe`), policies.py:44 (`claim_limit`) | `isinstance` chains over the same 3 policy classes in 3 operations | CONFIRMED, one finding | idiom: `functools.singledispatch` per operation, or `match` over the closed set |
| PY-P2 | GoF | P | factory-method | claims.py:64, claims.py:72, claims.py:80 (creation at claims.py:66, 74, 82) | identical `process` bodies except the assessor created | CONFIRMED | idiom: one `ClaimProcessor` taking the assessor class or a factory callable |
| PY-P3 | GoF | P | builder | claims.py:25 (`Claim.__init__`, 9 positional params), calls claims.py:91-95 | `None` placeholders at every call | CONFIRMED | idiom: `@dataclass(kw_only=True)` with defaults |
| PY-P4 | GoF | P | null-object | claims.py:38, claims.py:44, claims.py:47 | `claim.adjuster is not None` at 3 sites | CONFIRMED | a `NullAdjuster` used when no adjuster is assigned |
| PY-P5 | DRY | P | duplicated-logic-across-layers | policies.py:64-65 (`parse_claim_form`), policies.py:70-71 (`ClaimRecord`) | the claim amount rule (above 0, at most 250000) in the form layer and the model, with different messages and number forms | CONFIRMED | one `validate_claim_amount(amount)` (or one `MAX_CLAIM_AMOUNT`) both call |
| PY-P6 | SOLID | P | dip | policies.py:96 (`SmtpClient(...)` built in `ClaimReminder.__init__`), policies.py:99 (`datetime.now()`) | business class builds its mail client and reads the clock | CONFIRMED | pass the client and a `today` callable into `ClaimReminder`; build them at startup; no Protocol needed |
| PY-P7 | KISS | P | flat-over-nested | policies.py:75-84 (`payout`) | 4 nested levels, result variable returned at the end | CONFIRMED | guards returning 0.0, then `min(amount - deductible, limit)` |
| PY-A1 | KISS | A | pattern-overuse (also accept SOLID dip) | claims.py:6-15 (`AuditLog.__new__`), used at claims.py:41, 69, 77, 85 | `_instance` singleton created inside functions that never receive it | CONFIRMED | create one `AuditLog` at startup and pass it in; delete `__new__` |
| PY-D1 | GoF | D | value lookup | policies.py:53-60 (`tax_rate`) | `if/elif` chain on region | REJECTED: returns constants, 3 cases | none |
| PY-D2 | GoF | D | flag, 2 cases | claims.py:49-50 (`format_amount(..., with_symbol)`) | bool parameter | REJECTED: two stable cases | none |
| PY-D3 | DRY | D | knowledge-not-text | policies.py:104-105 (`MAX_PHOTOS_PER_CLAIM`, `REVIEW_SLA_DAYS`, both 10) | repeated literal | REJECTED: named, equal by coincidence | none |
| PY-D4 | SOLID | D | srp | policies.py:107-125 (`Period`) | class with many methods | REJECTED: cohesive value type | none |
| PY-D5 | KISS | D | pattern-overuse | policies.py:127-139 (`Notifier`, `EmailNotifier`, `SmsNotifier`) | Protocol | REJECTED: two real implementations, both used | none |

Not penalised: the `14` days in `ClaimReminder.remind` (policies.py:100) reported as a DRY magic value.

## Totals

| Family | P | A | D | Items to find (P + A) |
|---|---|---|---|---|
| GoF | 28 | 0 | 14 | 28 |
| DRY | 7 | 0 | 7 | 7 |
| KISS | 3 | 11 | 7 | 14 |
| SOLID | 7 | 0 | 7 | 7 |
| All | 45 | 11 | 35 | 56 |
