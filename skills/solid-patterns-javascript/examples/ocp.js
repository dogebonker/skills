'use strict';

// OCP: add a payment method without editing the fee calculation. Both versions agree.

// --- Violation: every new payment method is another edit to this switch.
const feeCentsV1 = ({ method, amountCents }) => {
  switch (method) {
    case 'card':
      return Math.round(amountCents * 0.029) + 30;
    case 'bank':
      return 50;
    case 'wallet':
      return Math.round(amountCents * 0.015);
    default:
      throw new Error(`unknown payment method: ${method}`);
  }
};

// --- Fix: fee rules are an object of functions; feeCents stays closed, the table is open.
const defaultFeeRules = Object.freeze({
  card: (cents) => Math.round(cents * 0.029) + 30,
  bank: () => 50,
  wallet: (cents) => Math.round(cents * 0.015),
});

const feeCents = ({ method, amountCents }, rules = defaultFeeRules) => {
  const rule = Object.hasOwn(rules, method) ? rules[method] : undefined;
  if (!rule) throw new Error(`unknown payment method: ${method}`);
  return rule(amountCents);
};

module.exports = { feeCentsV1, defaultFeeRules, feeCents };

if (require.main === module) {
  for (const method of ['card', 'bank', 'wallet']) {
    const p = { method, amountCents: 12000 };
    console.log(method, 'violation:', feeCentsV1(p), 'fix:', feeCents(p), 'same output:', feeCentsV1(p) === feeCents(p));
  }
  // Extension: a new method is a new entry passed in by the caller. feeCents is untouched.
  const withVoucher = { ...defaultFeeRules, voucher: () => 0 };
  console.log('voucher fix:', feeCents({ method: 'voucher', amountCents: 12000 }, withVoucher));
  // Object.hasOwn keeps inherited keys such as 'toString' from matching.
  try {
    feeCents({ method: 'toString', amountCents: 1 });
  } catch (e) {
    console.log('fix rejects:', e.message);
  }
}
