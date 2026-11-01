export {};

// Data normalization: the customer's email was copied onto every order row.
// The fix stores it once on the customer and orders keep only the customer id.

// --- Violation: denormalized rows, one copy per order ---
interface FlatOrder {
  orderId: number;
  customerId: number;
  customerEmail: string;
  totalCents: number;
}
const flatOrders: FlatOrder[] = [
  { orderId: 1, customerId: 7, customerEmail: "ana@old.example", totalCents: 1200 },
  { orderId: 2, customerId: 7, customerEmail: "ana@old.example", totalCents: 4500 },
  { orderId: 3, customerId: 9, customerEmail: "rui@example.com", totalCents: 800 },
];
function changeEmailFlat(customerId: number, email: string): number {
  let rowsTouched = 0;
  for (const o of flatOrders) {
    if (o.customerId === customerId) {
      o.customerEmail = email; // miss one row and the copies disagree
      rowsTouched++;
    }
  }
  return rowsTouched;
}
const emailForOrderFlat = (orderId: number) => flatOrders.find((o) => o.orderId === orderId)?.customerEmail;

// --- Fix: each fact stored once, joined on read ---
interface Customer {
  id: number;
  email: string;
}
interface Order {
  orderId: number;
  customerId: number;
  totalCents: number;
}
const customers = new Map<number, Customer>([
  [7, { id: 7, email: "ana@old.example" }],
  [9, { id: 9, email: "rui@example.com" }],
]);
const orders: Order[] = [
  { orderId: 1, customerId: 7, totalCents: 1200 },
  { orderId: 2, customerId: 7, totalCents: 4500 },
  { orderId: 3, customerId: 9, totalCents: 800 },
];
function changeEmail(customerId: number, email: string): number {
  const customer = customers.get(customerId);
  if (!customer) return 0;
  customer.email = email;
  return 1;
}
function emailForOrder(orderId: number): string | undefined {
  const order = orders.find((o) => o.orderId === orderId);
  return order ? customers.get(order.customerId)?.email : undefined;
}

// --- Demo: same reads; the update touches one row instead of every copy ---
console.log("rows touched:", changeEmailFlat(7, "ana@new.example"), "vs", changeEmail(7, "ana@new.example"));
for (const id of [1, 2, 3]) {
  const before = emailForOrderFlat(id);
  const after = emailForOrder(id);
  console.log(id, after, before === after ? "same" : "DIFFERENT");
}
