'use strict';

// DIP: the order policy receives the notifier it needs; the SMS detail plugs in. Same output.

// A low-level detail. In a real app this lives in its own module (infra/sms.js).
// Every line the gateway sends, so the demo can compare the two versions.
const smsLog = [];
const smsGateway = {
  send: (phone, text) => {
    const line = `  [sms ${phone}] ${text}`;
    smsLog.push(line);
    console.log(line);
  },
};

const confirmation = (order) => `Order ${order.id} confirmed: ${(order.totalCents / 100).toFixed(2)}`;

// --- Violation: business policy reaches for a concrete module-level transport.
const placeOrderV1 = (order) => {
  smsGateway.send(order.phone, confirmation(order));
  return order.id;
};

// --- Fix: the policy states the dependency it needs as a parameter and gets it injected.
const createOrderService = ({ notifyOrderConfirmed }) => ({
  place(order) {
    notifyOrderConfirmed(order.phone, confirmation(order));
    return order.id;
  },
});

module.exports = { placeOrderV1, createOrderService };

if (require.main === module) {
  const order = { id: 'A-1042', phone: '+351900000000', totalCents: 3599 };
  console.log('violation:');
  placeOrderV1(order);
  const violationSent = smsLog.splice(0);

  // Composition root: the only place that knows the concrete detail.
  console.log('fix:');
  createOrderService({ notifyOrderConfirmed: smsGateway.send }).place(order);
  const fixSent = smsLog.splice(0);
  console.log('same output:', JSON.stringify(violationSent) === JSON.stringify(fixSent));

  // A test swaps the detail without module mocking.
  const sent = [];
  createOrderService({ notifyOrderConfirmed: (_phone, text) => sent.push(text) }).place(order);
  console.log('fix with fake:', sent);
}
