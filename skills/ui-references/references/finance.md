# Finance and crypto references

Read this catalogue when the target involves banking, payments, business finance, investments, wallets or trading. Retrieved 2026-11-04 from first-party sources. No paid reference-library subscription is required.

Start with **Mercury + Wise + Stripe** for calm money movement and operations; **Rainbow + Phantom + Uniswap** for consumer wallets and swaps; **Kraken Pro** for intentionally dense trading work. These are flow-specific starting points. Preserve the product's own design kit.

The linked public demos, help articles and product media provide free research entry points. A product's live account may still require sign-in or eligibility. Never create a financial account, connect a funded wallet, submit a transaction or upload a real ID solely to inspect a design. Public demo interaction and official screenshots can answer most layout questions.

This is a source-backed shortlist, not a completed visual audit. “Borrow” is a proposed design application based on documented flows; verify the current images before treating it as evidence. Smoothness and motion require live interaction or video, not screenshots alone.

Priority **A** means search early for this user's preferred direction; **B** means useful when the named flow fits; **C** means specialist comparison. These are research priorities, not measured quality scores. Source links establish the feature or available evidence; inspect current captures before adopting the visual execution.

### Banking, transfers and personal finance

| Priority / product | Domain and platform | Specific patterns to study | Free access and limits | Verified source |
| --- | --- | --- | --- | --- |
| A — Mercury | Business banking; web | Account overview, transaction table, recipients, role configuration, money movement | Public JS demo is explicitly ungated; do not treat a US business context as universal | [Demo](https://demo.mercury.com/), [why the public demo exists](https://mercury.com/blog/designing-in-the-open), [roles demo guide](https://support.mercury.com/hc/en-us/articles/28768978787860-Understanding-roles-and-permissions) |
| A — Wise | Cross-border payments; web/mobile | Sender versus recipient amount entry, fees and ETA before confirmation, transfer tracking and delay explanation | Help is public; live account flows require access. Design-doc root redirected to 404 during this research, so use actual flow evidence | [Send money](https://wise.com/help/articles/2977959/how-do-i-send-money-with-wise/cvfjkcjopx), [track transfer](https://wise.com/help/articles/2977947/how-do-i-track-my-transfer) |
| B — Monzo | Consumer banking; mobile | Named savings/budget pots, add/withdraw actions, goals, salary allocation | Product navigation differs by region/version; avoid assuming historical Pots placement is current | [Pots help](https://monzo.com/ie/help/managing-money/help-pots), [Salary Sorter](https://monzo.com/features/monzo-payday) |
| B — Revolut | Multi-currency consumer banking; mobile | Balance/account switching, primary money actions, configurable overview | Linked redesign is historical (2023), not proof of the current UI; resist carrying super-app feature breadth into a focused product | [Revolut 10 design explanation](https://www.revolut.com/blog/post/revolut-10/) |
| B — N26 | Consumer banking; mobile | Purposeful subaccounts, savings targets, moving money between buckets, locked states | Region/plan-specific; drag gestures need accessible alternatives in our product | [Spaces](https://support.n26.com/en-fr/app-and-features/spaces/how-does-spaces-work?flags=noscript) |
| A — Cash App | Person-to-person payments; mobile | Amount-first task entry, recipient identification, request link handoff | Inspect payment confirmation and error states too; do not copy instant-send assumptions for irreversible crypto transfers | [Send and receive walkthrough](https://cash.app/learn/getting-started/how-to-send-and-receive-money) |
| B — Betterment | Investment management; mobile | Net-worth overview, goal/account distinction, performance drill-down and allocation editing | Useful for long-horizon investing, not a live trading terminal; account required for live UI | [Mobile portfolio management](https://www.betterment.com/help/mobile-investment-management) |

### Business spend, merchant payments and onboarding

| Priority / product | Domain and platform | Specific patterns to study | Free access and limits | Verified source |
| --- | --- | --- | --- | --- |
| A — Stripe Checkout | Merchant checkout; responsive web | Payment method selection, compact validated forms, localized errors, order context, confirmation | Public product/demo links; borrow task flow rather than Stripe's marketing page | [Checkout](https://stripe.com/payments/checkout) |
| A — Ramp | Spend management; web/mobile | Spend overview, cards, receipts, policy exceptions, approval queues | Public JS product tour; actual account actions require access | [Interactive product tour](https://ramp.com/explore-product), [product overview](https://ramp.com/why) |
| B — Brex | Travel and expenses; web/mobile | Trip/expense context, employee versus manager tasks, spending limits and reimbursements | Product page links an interactive demo; live account access is separate | [Travel and expense product/demo](https://www.brex.com/product/travel-expense-management) |
| B — Pleo | Team spending; web/mobile | Cards overview, receipt collection, employee expense follow-up, cash management | Official page offers an interactive demo without sign-up; sales-demo forms are a separate option | [Demo entry](https://www.pleo.io/en/demo/cashmanagement) |
| B — Airwallex | Multi-currency business finance; web/mobile | Currency balances, local account details, employee cards, FX transfer workflow | Public introduction is staged/demo evidence; do not infer all live states | [Product video/demo](https://www.airwallex.com/en-eu/watch-demo) |
| B — Square Invoices | Merchant invoicing; web/mobile | Invoice composition, send/review lifecycle, quick-view detail panel, paid/unpaid actions | Help public; actual dashboard requires account and permissions | [Create/send invoices](https://squareup.com/help/us/en/article/8387-create-and-send-invoices), [manage sent invoices](https://squareup.com/help/ie/en/article/8387-create-and-send-invoices) |
| C — Adyen Customer Area | Enterprise payment operations; web | Payment list, reconciliation/report navigation, resource switching and team permissions | Dense operational reference; menu changed from July 2026, so avoid old screenshots | [New menu](https://docs.adyen.com/new-customer-area-menu), [Customer Area/access](https://docs.adyen.com/platforms/manage-access) |
| A — Plaid Link | Bank connection; embedded web/mobile | Institution search, consent sequencing, return-to-app handoff, localization | Connection UX, not full banking UI. Public docs/previews; production credentials unnecessary for design research | [Link overview](https://plaid.com/docs/link/), [customization previews](https://plaid.com/docs/link/customization/) |
| B — Stripe Identity | Identity verification; web/mobile flow | Preparation, document capture, selfie sequence, processing/outcome states | Public docs link a demo; use provided sample inputs and never upload real IDs for research | [Identity and demo link](https://docs.stripe.com/identity) |

### Crypto wallets, swaps, portfolios and trading

| Priority / product | Domain and platform | Specific patterns to study | Free access and limits | Verified source |
| --- | --- | --- | --- | --- |
| A — Coinbase / Coinbase Design System | Consumer crypto; web/mobile | Consistent asset rows, financial formatting, component states, responsive hierarchy | CDS is documented for React and React Native with examples; component quality is not proof of every product flow. Retain our own tokens | [CDS introduction and examples](https://cds.coinbase.com/getting-started/introduction) |
| A — Phantom | Multi-chain wallet; mobile/extension | Token selection, quote review, network/fee disclosure, price impact and slippage settings | Inspect current help flows; older swap blog instructions differ. Research must not submit transactions | [Swap flow](https://help.phantom.com/articles/5985106844435), [swap settings](https://help.phantom.com/articles/27085326202515) |
| A — Rainbow | Wallet; mobile/extension | Wallet switcher, token search, keyboard command menu, swap/bridge review | Colour/playfulness may be too expressive for banking; borrow interactions selectively. Watch/read-only flows useful | [Extension flow index](https://rainbow.me/support/extension), [command menu](https://rainbow.me/th/support/extension/cmd-k-and-ctrl-k), [mobile swaps](https://rainbow.me/hi-in/support/app/bridge-and-swap-tokens) |
| A — Uniswap | Token swaps; web/mobile | Two-asset amount composer, review step, advanced settings, clear pending/outcome feedback | Public web UI is available for inspection; wallet connection/trade not needed for basic layout study | [Interface entry](https://app.uniswap.org/), [settings with screenshots](https://support.uniswap.org/hc/en-us/articles/45320061462797-How-to-change-swap-deadlines-on-the-Uniswap-interface) |
| B — Rabby | EVM wallet; extension/mobile | Pre-sign transaction preview, changed balances, network context and risk presentation | Homepage establishes product/platform, but preview behavior should be verified in help/demo captures; do not rely on testimonials as validation | [Official product](https://rabby.io/) |
| B — Zerion | Multi-chain portfolio; web/mobile/extension | Portfolio summary, chain grouping, asset positions, activity and token drill-down | Public product previews and web entry; avoid selecting an unrelated person's wallet as demo data | [Product and web-app preview](https://zerion.io/) |
| C — Kraken Pro | Professional trading; web/mobile | Resizable panels, order form/book/chart relationship, selected market context, tooltips | Intentionally dense; use only when a pro trading task requires it, not as the default minimalist reference | [Interface guide, updated October 2026](https://support.kraken.com/au/articles/kraken-pro-trading-interface-guide), [layout walkthrough](https://support.kraken.com/articles/setting-up-a-versatile-layout-on-kraken-pro) |

## Choose references by the problem

| Task | Start with | Search/example request | What the selected evidence must show |
| --- | --- | --- | --- |
| Bank transfer / remittance | Wise, Mercury, Revolut | “International transfer review with fees and arrival estimate” | Amount, recipient, exchange/fee context, review, pending and failure state |
| Checkout / pay-by-link | Stripe Checkout, Cash App, Square | “Payment link checkout confirmation” | Total, payment source, errors and completed payment handoff |
| KYC / bank connection | Stripe Identity, Plaid Link, Wise | “Identity verification document capture flow” | Before capture, permission/consent, retry, processing and outcome |
| Personal account overview | Wise, Monzo, N26 | “Banking home showing accounts and recent transactions” | Available balance hierarchy, meaningful primary actions, transaction grouping |
| Business approval workflow | Mercury, Ramp, Brex, Pleo | “Expense approval detail with receipt and policy exception” | Evidence beside decision, actor/role context, pending and approved states |
| Wallet portfolio | Coinbase, Rainbow, Zerion | “Crypto wallet portfolio with multiple networks” | Asset identity, balances, network context, empty and loading states |
| Swap / bridge | Uniswap, Phantom, Rainbow | “Crypto swap review with network fees and price impact” | Quoted amounts, route/network, minimum received or slippage, review and pending states |
| Signing / permissions | Rabby, Phantom | “Wallet transaction approval showing balance changes” | Consequences, affected assets, permissions and reject path |
| Professional trading | Kraken Pro | “Trading order form beside order book and chart” | Market context, precision, order states, useful density and responsive fallback |

Use these phrases to search official help centres, public product demos, videos or a connected reference service. Start broad enough to find alternatives, then inspect the actual screens. Keep the brand shortlist small per task.

## Capture checklist

1. Choose one primary product that solves the same user task, then one contrasting solution if a decision is still unclear.
2. Prefer the public demo or official help screenshots to the brand's landing page. Mark staged product renders and historical release posts.
3. Record the exact source URL, platform, date/version when known, state, local image path and decision informed by the reference.
4. Capture meaningful states: populated, empty, pending, error and success where applicable. Retain amount, fee, recipient, network and confirmation context when evaluating financial flows.
5. If the free source lacks a state, name that evidence gap; do not infer the live screen or acquire a subscription automatically.

## Evidence limits

No signed-in products, real financial actions or live motion were tested for this catalogue. Sources verify the named flow and available entry point, not a universal quality score. Product UI and access can change; re-open the selected source during a design task. Wise's design-doc root redirected to a 404 during research; use its verified help flows above. Famous brands are candidates, not blanket approval.
