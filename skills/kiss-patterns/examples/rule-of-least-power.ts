export {};

// Rule of least power: discount rules were stored as JavaScript source and executed.
// The fix stores them as plain data that a small function reads, so rules can be
// validated, listed in an admin page and diffed in review.

// --- Violation: rules are code strings run with full language power ---
const ruleSources = [
  "return total >= 10000 ? total * 0.10 : 0",
  "return items >= 5 ? 500 : 0",
];
const compiled = ruleSources.map((src) => new Function("total", "items", src) as (total: number, items: number) => number);
function discountV1(total: number, items: number): number {
  return Math.max(...compiled.map((rule) => rule(total, items)));
}

// --- Fix: declarative rules, the least powerful form that expresses them ---
type DiscountRule =
  | { kind: "percentOverTotal"; minTotalCents: number; percent: number }
  | { kind: "flatOverItems"; minItems: number; offCents: number };

const rules: readonly DiscountRule[] = [
  { kind: "percentOverTotal", minTotalCents: 10000, percent: 10 },
  { kind: "flatOverItems", minItems: 5, offCents: 500 },
];

function applyRule(rule: DiscountRule, total: number, items: number): number {
  switch (rule.kind) {
    case "percentOverTotal":
      return total >= rule.minTotalCents ? (total * rule.percent) / 100 : 0;
    case "flatOverItems":
      return items >= rule.minItems ? rule.offCents : 0;
  }
}
function discount(total: number, items: number): number {
  return Math.max(...rules.map((rule) => applyRule(rule, total, items)));
}

// --- Demo: same discounts; the data form can also be inspected ---
for (const [total, items] of [[4000, 1], [12000, 2], [3000, 6], [20000, 8]] as const) {
  const before = discountV1(total, items);
  const after = discount(total, items);
  console.log(total, items, after, before === after ? "same" : "DIFFERENT");
}
console.log("rule kinds:", rules.map((r) => r.kind).join(", "));
