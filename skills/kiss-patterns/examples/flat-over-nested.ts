export {};

// Flat over nested: guard clauses handle the special cases first and return,
// so the normal path reads last, at one indentation level.

interface Order {
  status: "paid" | "shipped" | "cancelled";
  paidCents: number;
  daysSinceDelivery: number | null;
  isGift: boolean;
}

// --- Violation: arrow-shaped nesting ---
function refundCentsV1(order: Order): number {
  let refund = 0;
  if (order.status !== "cancelled") {
    if (order.paidCents > 0) {
      if (order.daysSinceDelivery !== null) {
        if (order.daysSinceDelivery <= 30) {
          if (order.isGift) {
            refund = 0;
          } else {
            refund = order.paidCents;
          }
        }
      } else {
        refund = order.paidCents;
      }
    }
  }
  return refund;
}

// --- Fix: guard clauses, each ends the function ---
function refundCents(order: Order): number {
  if (order.status === "cancelled") return 0;
  if (order.paidCents <= 0) return 0;
  if (order.daysSinceDelivery === null) return order.paidCents;
  if (order.daysSinceDelivery > 30) return 0;
  if (order.isGift) return 0;
  return order.paidCents;
}

// --- Demo: same results over every combination ---
let checked = 0;
for (const status of ["paid", "shipped", "cancelled"] as const)
  for (const paidCents of [0, 2500])
    for (const daysSinceDelivery of [null, 10, 45])
      for (const isGift of [false, true]) {
        const order: Order = { status, paidCents, daysSinceDelivery, isGift };
        if (refundCentsV1(order) !== refundCents(order)) throw new Error(JSON.stringify(order));
        checked++;
      }
console.log(`refund rules agree on ${checked} orders`);
