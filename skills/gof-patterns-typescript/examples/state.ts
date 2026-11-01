export {};

// State: a discriminated union plus an exhaustive switch replaces State subclasses.
type Order =
  | { status: "pending" }
  | { status: "paid"; paidAt: number }
  | { status: "shipped"; paidAt: number; tracking: string }
  | { status: "cancelled" };

type OrderEvent = { type: "pay"; at: number } | { type: "ship"; tracking: string } | { type: "cancel" };

function transition(order: Order, event: OrderEvent): Order {
  switch (order.status) {
    case "pending":
      if (event.type === "pay") return { status: "paid", paidAt: event.at };
      if (event.type === "cancel") return { status: "cancelled" };
      break;
    case "paid":
      if (event.type === "ship") return { status: "shipped", paidAt: order.paidAt, tracking: event.tracking };
      break;
    case "shipped":
    case "cancelled":
      break;
    default: {
      const unreachable: never = order;
      return unreachable;
    }
  }
  throw new Error(`cannot ${event.type} when ${order.status}`);
}

let order: Order = { status: "pending" };
order = transition(order, { type: "pay", at: 1700000000 });
order = transition(order, { type: "ship", tracking: "TRK-42" });
console.log(order);
try {
  transition(order, { type: "cancel" });
} catch (e) {
  console.log((e as Error).message);
}
