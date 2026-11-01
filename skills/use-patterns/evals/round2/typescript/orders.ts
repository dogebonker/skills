import { PercentFee, priceLine, type FeeRule } from './pricing.js';

export interface TicketOrder {
  id: string;
  tier: string;
  quantity: number;
  unitCents: number;
  paymentMethod: string;
  refunded: boolean;
}

export interface EventInfo {
  name: string;
  currency: string;
  capacity: number;
}

export interface PaymentEvent {
  orderId: string;
  amountCents: number;
  succeeded: boolean;
}

const CARD_FEE = new PercentFee(3);
const PROMOTER_SHARE = 0.85;
const LOW_SALES_SHARE = 0.25;
const GROUP_SIZE = 10;

export class FlatFee implements FeeRule {
  constructor(private readonly cents: number) {}

  apply(): number {
    return this.cents;
  }
}

export function parseWebhookPayload(body: unknown): PaymentEvent {
  if (typeof body !== 'object' || body === null) throw new Error('webhook body is not an object');
  const data = body as Record<string, unknown>;
  const orderId = typeof data.order_ref === 'string' ? data.order_ref : '';
  const amountCents = typeof data.amount === 'number' ? Math.round(data.amount) : 0;
  const succeeded = typeof data.outcome === 'string' && data.outcome === 'paid';
  if (!orderId) throw new Error('webhook without order reference');
  return { orderId, amountCents, succeeded };
}

function formatTicketPrice(cents: number, currency: string): string {
  return `${(cents / 100).toFixed(2)} ${currency}`;
}

function discountTier(quantity: number): number {
  return quantity >= GROUP_SIZE ? 0.9 : 1;
}

export function groupDiscountPreview(orders: TicketOrder[]): number[] {
  return orders.map((order) => Math.round(order.quantity * order.unitCents * discountTier(order.quantity)));
}

export function bulkRefundQuote(orders: TicketOrder[]): number {
  return orders.reduce((sum, order) => sum + order.quantity * order.unitCents * discountTier(order.quantity), 0);
}

export function isCash(order: TicketOrder): boolean {
  return order.paymentMethod.trim().toLowerCase() === 'cash';
}

export function settleEventSales(event: EventInfo, orders: TicketOrder[], payments: PaymentEvent[]) {
  const paidIds = new Set(payments.filter((payment) => payment.succeeded).map((payment) => payment.orderId));
  const issues: string[] = [];
  const valid: TicketOrder[] = [];
  for (const order of orders) {
    if (order.quantity <= 0) {
      issues.push(`order ${order.id} has no tickets`);
      continue;
    }
    if (!isCash(order) && !paidIds.has(order.id)) {
      issues.push(`order ${order.id} has no confirmed payment`);
      continue;
    }
    valid.push(order);
  }

  const soldByTier = new Map<string, number>();
  let refundedTickets = 0;
  for (const order of valid) {
    if (order.refunded) {
      refundedTickets += order.quantity;
      continue;
    }
    soldByTier.set(order.tier, (soldByTier.get(order.tier) ?? 0) + order.quantity);
  }
  const sold = [...soldByTier.values()].reduce((sum, count) => sum + count, 0);
  const fillRate = event.capacity ? sold / event.capacity : 0;
  if (sold > event.capacity) issues.push(`oversold by ${sold - event.capacity}`);

  let grossCents = 0;
  let feeCents = 0;
  let refundCents = 0;
  for (const order of valid) {
    const subtotal = order.quantity * order.unitCents;
    if (order.refunded) {
      refundCents += subtotal;
      continue;
    }
    grossCents += subtotal;
    if (order.paymentMethod === 'cash') continue;
    feeCents += CARD_FEE.apply(subtotal);
  }

  const netCents = grossCents - feeCents;
  const promoterCents = Math.round(netCents * PROMOTER_SHARE);
  const venueCents = netCents - promoterCents;
  const lowSales = fillRate < LOW_SALES_SHARE;
  const averageCents = sold ? Math.round(grossCents / sold) : 0;
  let cashTickets = 0;
  for (const order of valid) {
    if (isCash(order) && !order.refunded) cashTickets += order.quantity;
  }

  const lines = [
    `Settlement for ${event.name}`,
    `Tickets sold: ${sold} of ${event.capacity} (${Math.round(fillRate * 100)}%)`,
  ];
  for (const [tier, count] of [...soldByTier.entries()].sort()) lines.push(`  ${tier}: ${count}`);
  lines.push(priceLine('Gross', grossCents, event.currency));
  lines.push(priceLine('Card fees', feeCents, event.currency));
  lines.push(priceLine('Refunded', refundCents, event.currency));
  lines.push(priceLine('Promoter payout', promoterCents, event.currency));
  lines.push(priceLine('Venue share', venueCents, event.currency));
  lines.push(priceLine('Average ticket', averageCents, event.currency));
  lines.push(`Paid in cash: ${cashTickets} tickets`);
  if (refundedTickets) lines.push(`Refunded tickets: ${refundedTickets}`);
  if (lowSales) lines.push('Low sales: review marketing spend');
  for (const issue of issues) lines.push(`Check: ${issue}`);

  const exportRow = {
    event: event.name,
    currency: currencyNames()[event.currency] ?? event.currency,
    sold,
    gross: grossCents,
    fees: feeCents,
    refunds: refundCents,
    promoter: promoterCents,
    venue: venueCents,
    average: averageCents,
    cash: cashTickets,
  };
  return { lines, exportRow, issues };
}

export function currencyNames(): Record<string, string> {
  return {
    USD: 'US dollar',
    EUR: 'Euro',
    GBP: 'Pound sterling',
    JPY: 'Japanese yen',
    CHF: 'Swiss franc',
    CAD: 'Canadian dollar',
    AUD: 'Australian dollar',
    NZD: 'New Zealand dollar',
    SEK: 'Swedish krona',
    NOK: 'Norwegian krone',
    DKK: 'Danish krone',
    PLN: 'Polish zloty',
    CZK: 'Czech koruna',
    HUF: 'Hungarian forint',
    RON: 'Romanian leu',
    BGN: 'Bulgarian lev',
    ISK: 'Icelandic krona',
    TRY: 'Turkish lira',
    UAH: 'Ukrainian hryvnia',
    ILS: 'Israeli new shekel',
    AED: 'UAE dirham',
    SAR: 'Saudi riyal',
    QAR: 'Qatari riyal',
    KWD: 'Kuwaiti dinar',
    BHD: 'Bahraini dinar',
    OMR: 'Omani rial',
    JOD: 'Jordanian dinar',
    EGP: 'Egyptian pound',
    MAD: 'Moroccan dirham',
    TND: 'Tunisian dinar',
    ZAR: 'South African rand',
    NGN: 'Nigerian naira',
    KES: 'Kenyan shilling',
    GHS: 'Ghanaian cedi',
    ETB: 'Ethiopian birr',
    TZS: 'Tanzanian shilling',
    UGX: 'Ugandan shilling',
    INR: 'Indian rupee',
    PKR: 'Pakistani rupee',
    BDT: 'Bangladeshi taka',
    LKR: 'Sri Lankan rupee',
    NPR: 'Nepalese rupee',
    CNY: 'Chinese yuan',
    HKD: 'Hong Kong dollar',
    TWD: 'New Taiwan dollar',
    KRW: 'South Korean won',
    SGD: 'Singapore dollar',
    MYR: 'Malaysian ringgit',
    THB: 'Thai baht',
    IDR: 'Indonesian rupiah',
    PHP: 'Philippine peso',
    VND: 'Vietnamese dong',
    MXN: 'Mexican peso',
    BRL: 'Brazilian real',
    ARS: 'Argentine peso',
    CLP: 'Chilean peso',
    COP: 'Colombian peso',
    PEN: 'Peruvian sol',
    UYU: 'Uruguayan peso',
    BOB: 'Bolivian boliviano',
    PYG: 'Paraguayan guarani',
    DOP: 'Dominican peso',
    CRC: 'Costa Rican colon',
    GTQ: 'Guatemalan quetzal',
    JMD: 'Jamaican dollar',
    TTD: 'Trinidad and Tobago dollar',
    XOF: 'West African CFA franc',
    XAF: 'Central African CFA franc',
    AOA: 'Angolan kwanza',
    MZN: 'Mozambican metical',
    CVE: 'Cape Verdean escudo',
    GEL: 'Georgian lari',
    AMD: 'Armenian dram',
    AZN: 'Azerbaijani manat',
    KZT: 'Kazakhstani tenge',
    UZS: 'Uzbekistani som',
    MNT: 'Mongolian togrog',
    RSD: 'Serbian dinar',
    MKD: 'Macedonian denar',
    ALL: 'Albanian lek',
  };
}

const orders: TicketOrder[] = [
  { id: 'T1', tier: 'standing', quantity: 4, unitCents: 3500, paymentMethod: 'card', refunded: false },
  { id: 'T2', tier: 'seated', quantity: 2, unitCents: 5500, paymentMethod: ' Cash', refunded: false },
  { id: 'T3', tier: 'standing', quantity: 1, unitCents: 3500, paymentMethod: 'card', refunded: true },
];
const payments = [parseWebhookPayload({ order_ref: 'T1', amount: 14000, outcome: 'paid' })];
const result = settleEventSales({ name: 'Harbour Lights', currency: 'EUR', capacity: 400 }, orders, payments);
console.log(result.lines.join('\n'), result.exportRow, new FlatFee(150).apply());
