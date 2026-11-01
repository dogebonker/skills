export {};

// OCP: add a payment method without editing the fee calculation. Both versions agree.

type Payment = { method: string; amountCents: number };

// --- Violation: every new payment method is another edit to this switch.
function feeCentsV1(p: Payment): number {
  switch (p.method) {
    case "card":
      return Math.round(p.amountCents * 0.029) + 30;
    case "bank":
      return 50;
    case "wallet":
      return Math.round(p.amountCents * 0.015);
    default:
      throw new Error(`unknown payment method: ${p.method}`);
  }
}

// --- Fix: fee rules are a table of functions; feeCents stays closed, the table is open.
type FeeRule = (amountCents: number) => number;
type FeeRules = Readonly<Record<string, FeeRule>>;

const defaultFeeRules = {
  card: (cents) => Math.round(cents * 0.029) + 30,
  bank: () => 50,
  wallet: (cents) => Math.round(cents * 0.015),
} satisfies FeeRules;

function feeCents(p: Payment, rules: FeeRules = defaultFeeRules): number {
  const rule = Object.hasOwn(rules, p.method) ? rules[p.method] : undefined;
  if (!rule) throw new Error(`unknown payment method: ${p.method}`);
  return rule(p.amountCents);
}

const payments: Payment[] = [
  { method: "card", amountCents: 12000 },
  { method: "bank", amountCents: 12000 },
  { method: "wallet", amountCents: 12000 },
];
for (const p of payments) {
  console.log(p.method, "violation:", feeCentsV1(p), "fix:", feeCents(p), "same output:", feeCentsV1(p) === feeCents(p));
}

// Extension: a new method is a new entry, passed in by the caller. feeCents is untouched.
const withVoucher: FeeRules = { ...defaultFeeRules, voucher: () => 0 };
console.log("voucher fix:", feeCents({ method: "voucher", amountCents: 12000 }, withVoucher));
