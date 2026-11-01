export {};

// YAGNI: the shop sells in euros only, but the cart was built for every currency.
// The fix models what the business does today: integer euro cents.

// --- Violation: presumptive multi-currency support nobody uses ---
interface Money {
  amount: number;
  currency: string;
}
const exchangeRates: Record<string, number> = { EUR: 1 };
function convert(m: Money, to: string): Money {
  const rate = (exchangeRates[to] ?? 1) / (exchangeRates[m.currency] ?? 1);
  return { amount: Math.round(m.amount * rate), currency: to };
}
function cartTotalV1(lines: Array<{ price: Money; qty: number }>, displayCurrency = "EUR"): Money {
  let total = 0;
  for (const line of lines) total += convert(line.price, displayCurrency).amount * line.qty;
  return { amount: total, currency: displayCurrency };
}

// --- Fix: the simplest model of the current requirement ---
function cartTotalCents(lines: Array<{ priceCents: number; qty: number }>): number {
  return lines.reduce((sum, line) => sum + line.priceCents * line.qty, 0);
}

// --- Demo: same totals ---
const carts = [
  [{ priceCents: 1999, qty: 2 }, { priceCents: 450, qty: 1 }],
  [{ priceCents: 12000, qty: 1 }],
];
for (const cart of carts) {
  const before = cartTotalV1(cart.map((l) => ({ price: { amount: l.priceCents, currency: "EUR" }, qty: l.qty }))).amount;
  const after = cartTotalCents(cart);
  console.log(after, before === after ? "same" : "DIFFERENT");
}
