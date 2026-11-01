export {};

// The wrong abstraction: one shared formatter grew a flag per caller.
// The fix inlines it back into each caller and keeps only what that caller uses.

interface FormatOptions {
  forInvoice?: boolean;
  forEmail?: boolean;
  showCurrencyCode?: boolean;
  roundToWhole?: boolean;
}

// --- Violation: every new caller added a parameter and a branch ---
function formatPrice(cents: number, opts: FormatOptions = {}): string {
  let amount = cents / 100;
  if (opts.roundToWhole && !opts.forInvoice) amount = Math.round(amount);
  let text = opts.roundToWhole && !opts.forInvoice ? amount.toString() : amount.toFixed(2);
  if (opts.showCurrencyCode) text = `${text} EUR`;
  else text = `€${text}`;
  if (opts.forEmail) text = text.replace(".", ",");
  if (opts.forInvoice) text = `Total due: ${text}`;
  return text;
}

// --- Fix: each caller owns the few lines it actually needs ---
function invoiceTotal(cents: number): string {
  return `Total due: ${(cents / 100).toFixed(2)} EUR`;
}

function emailPrice(cents: number): string {
  return `€${(cents / 100).toFixed(2).replace(".", ",")}`;
}

function bannerPrice(cents: number): string {
  return `€${Math.round(cents / 100)}`;
}

// --- Demo: same strings before and after the re-inline ---
for (const cents of [1999, 25000, 49]) {
  const pairs: Array<[string, string, string]> = [
    ["invoice", formatPrice(cents, { forInvoice: true, showCurrencyCode: true }), invoiceTotal(cents)],
    ["email", formatPrice(cents, { forEmail: true }), emailPrice(cents)],
    ["banner", formatPrice(cents, { roundToWhole: true }), bannerPrice(cents)],
  ];
  for (const [caller, before, after] of pairs) {
    console.log(caller, before, "|", after, before === after ? "same" : "DIFFERENT");
  }
}
