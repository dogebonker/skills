export type SubscriptionStatus = 'trial' | 'active' | 'pastDue' | 'cancelled';

export class Subscription {
  status: SubscriptionStatus = 'trial';
  failedPayments = 0;

  constructor(readonly customerId: string) {}

  paymentSucceeded(): void {
    switch (this.status) {
      case 'trial':
      case 'pastDue':
        this.status = 'active';
        this.failedPayments = 0;
        break;
      case 'active':
        this.failedPayments = 0;
        break;
      case 'cancelled':
        throw new Error('subscription is cancelled');
    }
  }

  paymentFailed(): void {
    switch (this.status) {
      case 'trial':
        this.status = 'cancelled';
        break;
      case 'active':
        this.status = 'pastDue';
        this.failedPayments = 1;
        break;
      case 'pastDue':
        this.failedPayments += 1;
        if (this.failedPayments >= 3) this.status = 'cancelled';
        break;
    }
  }
}

export function statusLabel(status: SubscriptionStatus): string {
  switch (status) {
    case 'trial': return 'Free trial';
    case 'active': return 'Active';
    case 'pastDue': return 'Payment overdue';
    case 'cancelled': return 'Cancelled';
  }
}

interface InvoiceNumberGenerator { next(): string }
class SequentialInvoiceNumberGenerator implements InvoiceNumberGenerator {
  private counter = 1000;
  next(): string { return `INV-${++this.counter}`; }
}
export const invoiceNumbers: InvoiceNumberGenerator = new SequentialInvoiceNumberGenerator();

declare class AcmePayClient {
  chargeCard(req: { amount_cents: number; card_token: string; currency_code: string }): { status_code: number; txn_id: string };
  refundCharge(txnId: string, amountCents: number): { status_code: number };
}
const acme = new AcmePayClient();

export function chargeSubscription(sub: Subscription, priceEur: number, cardToken: string): string {
  const res = acme.chargeCard({ amount_cents: Math.round(priceEur * 100), card_token: cardToken, currency_code: 'EUR' });
  if (res.status_code !== 200) {
    sub.paymentFailed();
    throw new Error(`charge failed with ${res.status_code}`);
  }
  sub.paymentSucceeded();
  return `${invoiceNumbers.next()}:${res.txn_id}`;
}

export function chargeSetupFee(feeEur: number, cardToken: string): string {
  const res = acme.chargeCard({ amount_cents: Math.round(feeEur * 100), card_token: cardToken, currency_code: 'EUR' });
  if (res.status_code !== 200) throw new Error(`setup fee failed with ${res.status_code}`);
  return res.txn_id;
}

export function refund(txnId: string, amountEur: number): boolean {
  return acme.refundCharge(txnId, Math.round(amountEur * 100)).status_code === 200;
}

export function trialEndsAt(startedAtMs: number): number {
  return startedAtMs + 1209600000;
}

export function trialExpired(sub: Subscription, startedAtMs: number, nowMs: number): boolean {
  return sub.status === 'trial' && nowMs - startedAtMs > 1209600000;
}

export function nextRetryAt(failedAtSec: number, attempt: number): number {
  return failedAtSec + attempt * 259200;
}

export const MAX_SEATS_PER_PLAN = 30;
export const INVOICE_DUE_DAYS = 30;

export interface Notifier {
  notify(customerId: string, text: string): string;
}

export class EmailNotifier implements Notifier {
  notify(customerId: string, text: string): string { return `email to ${customerId}: ${text}`; }
}

export class SmsNotifier implements Notifier {
  notify(customerId: string, text: string): string { return `sms to ${customerId}: ${text.slice(0, 160)}`; }
}

export function notifierFor(preference: 'email' | 'sms'): Notifier {
  return preference === 'email' ? new EmailNotifier() : new SmsNotifier();
}

export function remindUnpaid(sub: Subscription, preference: 'email' | 'sms'): string {
  return notifierFor(preference).notify(sub.customerId, `Your invoice is due in ${INVOICE_DUE_DAYS} days`);
}
