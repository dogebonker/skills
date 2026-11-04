# Find matching references without a subscription

Adapted from Mobbin's MIT-licensed search workflow. See [upstream notices](../UPSTREAM.md). The search backend is replaceable; the evidence standard stays the same.

## Choose the evidence

| Need | Look for | Prefer |
| --- | --- | --- |
| Whole screen or component | Same job, platform, state and information density | A working product demo or actual application screenshot |
| Multi-step task | Entry, decisions, confirmation, waiting, failure and recovery | A recorded product walkthrough, help-centre sequence or accessible demo |
| Marketing section | The corresponding hero, pricing or feature section | A current public website |
| Interaction feel | Response, interruption, scrolling, focus and reduced motion | A live interaction or first-party video; a still image cannot establish smoothness |

Match the user's task before the aesthetic. Mobile and desktop examples are not interchangeable. Label cross-platform or cross-domain borrowing and limit it to the relevant structure.

## Sources, in order of fit and access

1. The user's supplied captures, saved files and explicitly chosen reference collection.
2. Existing local screens: `node <skill>/library.mjs search <product or pattern>`.
3. Public working demos and product walkthroughs. Use [the catalogue](catalogue.md) to identify candidates, then inspect the relevant screen.
4. First-party help articles, product docs, release posts and screenshot galleries. These often expose settings, errors and review states hidden behind sign-in.
5. Public source repositories' screenshot assets or videos, after verifying the repository belongs to the product. Read assets; do not execute downloaded code to collect references.
6. Official App Store / Play Store screenshots. Treat staged store imagery as marketing, not proof of every state.
7. Any already connected reference-search service, including Mobbin or Refero, when available and authorized. Tool names and arguments come from the live tool schema. No service, API key, paid account or installation is required by this workflow.

A login wall means choose another public source. Do not scrape restricted libraries, bypass access controls or imply that this reproduces Mobbin's private corpus. If a specific image cannot be accessed, record the gap and use another inspectable example.

## Query by the decision being made

Start with one screen, section or journey per query. Use plain language, the task's domain, and up to three relevant constraints. Split unrelated targets into separate searches.

Examples:

- `bank transfer review fee arrival time`
- `crypto wallet send review network fee`
- `business banking transactions pending state`
- `agent workspace changes review sidebar`
- `site:help.wise.com transfer review` or the equivalent product help domain
- `site:github.com <verified-product-repo> screenshots`

Run separate searches for the pattern and for a candidate product's treatment. Avoid asking search to solve taste with words such as “best premium beautiful”. Search results and brand reputations are leads, not visual evidence.

When results are weak, change the screen noun, state, domain or source. Repeating an unchanged query does not widen the evidence. Browse the source's neighbouring screens or article links when the sequence matters. A reference-service refusal should switch to public/local evidence; repeated paid calls cannot repair missing access.

## Inspect, then save

Open each image being cited at readable resolution. For a video, inspect the relevant segment and record timestamps. A page summary, alt text or image filename does not establish layout, contrast or interaction behaviour. Count distinct products, not screenshots of the same product.

Save selected images locally with their original source page:

`node <skill>/library.mjs add <file-or-public-image-url> --app <product> --flow <pattern> --platform <platform> --source <source-page> --note <state-and-date>`

Supported platforms: `web`, `web-phone`, `ios`, `ipad`, `mac`, `android`. For public live pages use `capture <url> --app <product> --flow <pattern> [--full|--selector <css>] [--phone]`. Store reference screenshots in the local library; target-app iterations use `--out` and stay on the board. Keep private account data out of the shared library.

Record the inspected asset, source URL, product, platform, state, capture/check date, and whether it is live UI, help/gallery evidence or staged marketing. Store a local file; image CDN links and signed URLs can expire. Respect the source's permitted use; link to original assets rather than republishing a product screenshot corpus.

## Select a coherent direction

Group examples by their structural solution. Choose the direction that answers the target's problems while fitting its existing kit. Usually a few inspected screens from two or more products suffice; one product is one example, not broad corroboration.

For each selected screen record **take** (the exact decision it demonstrates) and **leave** (brand, palette, copy, unrelated functionality). Keep one main direction; a secondary reference may solve a bounded detail, not introduce a competing layout system. Drop an attractive example if it does not show the needed decision.

If no suitable external screen is inspectable, continue only on observed problems, the existing product and the user's brief. Call the result best effort and name the missing reference coverage; do not claim a reference match or invent a screenshot.
