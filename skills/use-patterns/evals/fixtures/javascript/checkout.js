'use strict';

class MemoryDb {
  constructor() { this.rows = new Map(); }
  find(id) { return this.rows.get(id); }
  save(row) { this.rows.set(row.id, row); return row; }
  remove(id) { return this.rows.delete(id); }
}

class OrderRepository {
  constructor(db) {
    this.db = db;
  }
  find(id) {
    return this.db.find(id);
  }
  save(order) {
    return this.db.save(order);
  }
  remove(id) {
    return this.db.remove(id);
  }
}

class Order {
  constructor(id, customer, items, country, shippingMethod, giftWrap, giftMessage, couponCode, notes) {
    this.id = id;
    this.customer = customer;
    this.items = items;
    this.country = country;
    this.shippingMethod = shippingMethod;
    this.giftWrap = giftWrap;
    this.giftMessage = giftMessage;
    this.couponCode = couponCode;
    this.notes = notes;
    this.status = 'new';
  }
}

function currencyFor(country) {
  switch (country) {
    case 'US': return 'USD';
    case 'GB': return 'GBP';
    case 'JP': return 'JPY';
    default: return 'EUR';
  }
}

function formatPrice(amount, currency, compact) {
  if (compact) return `${Math.round(amount)} ${currency}`;
  return `${amount.toFixed(2)} ${currency}`;
}

function shippingCost(order) {
  const weight = order.items.reduce((sum, item) => sum + item.weightKg * item.qty, 0);
  switch (order.shippingMethod) {
    case 'standard':
      return weight < 2 ? 4.99 : 4.99 + (weight - 2) * 1.2;
    case 'express':
      return 9.99 + weight * 2.5;
    case 'overnight':
      return Math.max(24.99, weight * 4);
    case 'pickup':
      return 0;
    default:
      throw new Error(`unknown shipping method ${order.shippingMethod}`);
  }
}

function deliveryDays(order) {
  switch (order.shippingMethod) {
    case 'standard': return order.country === 'US' ? 5 : 9;
    case 'express': return order.country === 'US' ? 2 : 4;
    case 'overnight': return 1;
    case 'pickup': return 0;
    default: throw new Error(`unknown shipping method ${order.shippingMethod}`);
  }
}

function discountFor(customer, subtotal) {
  if (customer.loyalty) return subtotal * customer.loyalty.discountRate;
  return 0;
}

function pointsEarned(customer, total) {
  if (customer.loyalty) return Math.floor(total * customer.loyalty.pointsPerUnit);
  return 0;
}

function tierLabel(customer) {
  return customer.loyalty ? customer.loyalty.tier : 'none';
}

class CheckoutService {
  constructor(repository, mailer, inventory, analytics) {
    this.repository = repository;
    this.mailer = mailer;
    this.inventory = inventory;
    this.analytics = analytics;
  }

  total(order) {
    const subtotal = order.items.reduce((sum, item) => sum + item.price * item.qty, 0);
    return subtotal - discountFor(order.customer, subtotal) + shippingCost(order);
  }

  pay(orderId, paidAt) {
    const order = this.repository.find(orderId);
    const amount = this.total(order);
    order.status = 'paid';
    order.paidAt = paidAt;
    this.repository.save(order);
    this.mailer.send(order.customer.email, `Receipt ${order.id}: ${formatPrice(amount, currencyFor(order.country), false)}`);
    this.inventory.reserve(order.items);
    this.analytics.track('order_paid', { id: order.id, amount, points: pointsEarned(order.customer, amount) });
    return amount;
  }

  cancel(orderId) {
    const order = this.repository.find(orderId);
    order.status = 'cancelled';
    this.repository.save(order);
    this.mailer.send(order.customer.email, `Order ${order.id} cancelled`);
    this.inventory.release(order.items);
    this.analytics.track('order_cancelled', { id: order.id, tier: tierLabel(order.customer) });
  }
}

if (require.main === module) {
  const log = (...args) => console.log(...args);
  const repository = new OrderRepository(new MemoryDb());
  const service = new CheckoutService(
    repository,
    { send: (to, text) => log('mail', to, text) },
    { reserve: (items) => log('reserve', items.length), release: (items) => log('release', items.length) },
    { track: (event, data) => log('track', event, JSON.stringify(data)) },
  );
  const alice = { email: 'alice@example.com', loyalty: { discountRate: 0.1, pointsPerUnit: 2, tier: 'gold' } };
  const bob = { email: 'bob@example.com', loyalty: null };
  const items = [{ price: 20, qty: 2, weightKg: 1.5 }];
  repository.save(new Order('A-1001', alice, items, 'US', 'express', false, null, null, null));
  repository.save(new Order('A-1002', bob, items, 'GB', 'standard', true, 'Happy birthday', null, 'leave at door'));
  log(service.pay('A-1001', '2026-10-01'), deliveryDays(repository.find('A-1001')));
  service.cancel('A-1002');
  log(formatPrice(12.5, currencyFor('JP'), true));
}

module.exports = { Order, CheckoutService, OrderRepository, shippingCost, deliveryDays };

const SKU_PATTERN = /^[A-Z]{2}\d{4}$/;
const VOUCHER_PATTERN = /^[A-Z]{2}\d{4}$/;
const isSku = (code) => SKU_PATTERN.test(code);
const isVoucher = (code) => VOUCHER_PATTERN.test(code);

function validateAddress(address) {
  if (!['US', 'GB', 'JP', 'PT'].includes(address.country)) throw new Error(`we do not ship to ${address.country}`);
  return address;
}

function countryOptions() {
  return [
    { value: 'US', label: 'United States' },
    { value: 'GB', label: 'United Kingdom' },
    { value: 'JP', label: 'Japan' },
    { value: 'PT', label: 'Portugal' },
  ];
}

const DAY_MS = 24 * 60 * 60 * 1000;
const REFUND_WINDOW_DAYS = 30;
const GIFT_WRAP_FEE = 2.5;

function refundAmount(order, paidAmount, now) {
  let amount = 0;
  if (order.status !== 'cancelled') {
    if (order.paidAt) {
      if ((now - new Date(order.paidAt)) / DAY_MS <= REFUND_WINDOW_DAYS) {
        if (order.giftWrap) {
          amount = paidAmount - GIFT_WRAP_FEE;
        } else {
          amount = paidAmount;
        }
      }
    }
  }
  return amount;
}

class PaymentsHttpClient {
  constructor(baseUrl, apiKey) { this.baseUrl = baseUrl; this.apiKey = apiKey; }
  refund(paymentId, amount) { return { id: `rf_${paymentId}`, amount, url: `${this.baseUrl}/refunds` }; }
}

class RefundService {
  constructor() {
    this.payments = new PaymentsHttpClient('https://payments.example.com', process.env.PAYMENTS_KEY);
  }

  refund(order, paidAmount) {
    const amount = refundAmount(order, paidAmount, new Date());
    return amount > 0 ? this.payments.refund(order.id, amount) : null;
  }
}

class Money {
  #cents;
  constructor(cents, currency) { this.#cents = Math.round(cents); this.currency = currency; }
  get cents() { return this.#cents; }
  plus(other) { return new Money(this.#cents + this.#same(other).cents, this.currency); }
  minus(other) { return new Money(this.#cents - this.#same(other).cents, this.currency); }
  times(factor) { return new Money(this.#cents * factor, this.currency); }
  isZero() { return this.#cents === 0; }
  compare(other) { return Math.sign(this.#cents - this.#same(other).cents); }
  equals(other) { return other.currency === this.currency && other.cents === this.#cents; }
  allocate(parts) { const base = Math.floor(this.#cents / parts); return Array.from({ length: parts }, (_, i) => new Money(base + (i < this.#cents % parts ? 1 : 0), this.currency)); }
  toString() { return `${(this.#cents / 100).toFixed(2)} ${this.currency}`; }
  #same(other) { if (other.currency !== this.currency) throw new Error('currency mismatch'); return other; }
}

function importItems(rows, onProgress = () => {}) {
  const items = [];
  rows.forEach((row, i) => {
    items.push({ price: Number(row.price), qty: Number(row.qty), weightKg: Number(row.weightKg) });
    onProgress(i + 1, rows.length);
  });
  return items;
}

if (require.main === module) {
  const items = importItems([{ price: '20', qty: '1', weightKg: '1.5' }], (done, total) => console.log(`imported ${done}/${total}`));
  const order = { id: 'A-1003', status: 'paid', paidAt: '2026-10-20', giftWrap: true, items };
  console.log(new RefundService().refund(order, 20), validateAddress({ country: 'PT' }), countryOptions().length);
  console.log(isSku('AB1234'), isVoucher('XY9999'), new Money(1000, 'EUR').plus(new Money(250, 'EUR')).allocate(3).join(' | '));
}
