export {};

// DIP: the order policy owns the abstraction it needs; the SMS detail plugs in. Same output.

type Order = { id: string; phone: string; totalCents: number };

// Every line the gateway sends, so the demo can compare the two versions.
const smsLog: string[] = [];

class SmsGateway {
  send(phone: string, text: string): void {
    const line = `  [sms ${phone}] ${text}`;
    smsLog.push(line);
    console.log(line);
  }
}

// --- Violation: business policy constructs and depends on a concrete transport.
class OrderServiceV1 {
  readonly #sms = new SmsGateway();

  place(order: Order): string {
    const text = `Order ${order.id} confirmed: ${(order.totalCents / 100).toFixed(2)}`;
    this.#sms.send(order.phone, text);
    return order.id;
  }
}

// --- Fix: the policy declares the port it needs and receives an implementation.
interface OrderNotifier {
  orderConfirmed(phone: string, text: string): void;
}

class OrderService {
  readonly #notifier: OrderNotifier;

  constructor(notifier: OrderNotifier) {
    this.#notifier = notifier;
  }

  place(order: Order): string {
    const text = `Order ${order.id} confirmed: ${(order.totalCents / 100).toFixed(2)}`;
    this.#notifier.orderConfirmed(order.phone, text);
    return order.id;
  }
}

// Composition root: the only place that knows the concrete detail.
const gateway = new SmsGateway();
const smsNotifier: OrderNotifier = { orderConfirmed: (phone, text) => gateway.send(phone, text) };

const order: Order = { id: "A-1042", phone: "+351900000000", totalCents: 3599 };
console.log("violation:");
new OrderServiceV1().place(order);
const violationSent = smsLog.splice(0);
console.log("fix:");
new OrderService(smsNotifier).place(order);
const fixSent = smsLog.splice(0);
console.log("same output:", JSON.stringify(violationSent) === JSON.stringify(fixSent));

// A test swaps the detail without touching OrderService.
const sent: string[] = [];
new OrderService({ orderConfirmed: (_phone, text) => sent.push(text) }).place(order);
console.log("fix with fake:", sent);
