export {};

// Single source of truth: the list of order statuses lives in one array; the type,
// the dropdown options and the runtime check are all derived from it.

// --- Violation: the same list written three times, free to drift apart ---
type LegacyStatus = "pending" | "paid" | "shipped" | "cancelled";
const legacyDropdown = ["pending", "paid", "shipped", "cancelled"];
function legacyIsStatus(value: string): value is LegacyStatus {
  return value === "pending" || value === "paid" || value === "shipped" || value === "cancelled";
}

// --- Fix: one array, everything else derived ---
const ORDER_STATUSES = ["pending", "paid", "shipped", "cancelled"] as const;
type OrderStatus = (typeof ORDER_STATUSES)[number];
const dropdown: readonly OrderStatus[] = ORDER_STATUSES;
function isOrderStatus(value: string): value is OrderStatus {
  return (ORDER_STATUSES as readonly string[]).includes(value);
}

// The derived type still catches typos at compile time.
const firstShipped: OrderStatus = "shipped";

// --- Demo: both versions accept and reject the same inputs ---
for (const input of ["paid", "shipped", "refunded", ""]) {
  console.log(JSON.stringify(input), "violation:", legacyIsStatus(input), "fix:", isOrderStatus(input));
}
console.log("dropdowns equal:", JSON.stringify(legacyDropdown) === JSON.stringify(dropdown), firstShipped);
