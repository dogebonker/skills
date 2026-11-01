export interface FeeRule {
  apply(subtotalCents: number): number;
}

export class PercentFee implements FeeRule {
  constructor(private readonly percent: number) {}

  apply(subtotalCents: number): number {
    return Math.round((subtotalCents * this.percent) / 100);
  }
}

export const EARLY_BIRD_CUTOFFS: ReadonlyArray<[number, number]> = [
  [60, 0.8],
  [30, 0.9],
];

export function earlyBirdRate(daysBefore: number): number {
  const match = EARLY_BIRD_CUTOFFS.find(([days]) => daysBefore >= days);
  return match ? match[1] : 1;
}

export function formatTicketPrice(cents: number, currency: string): string {
  if (!Number.isInteger(cents)) throw new Error(`price must be whole cents, got ${cents}`);
  return `${(cents / 100).toFixed(2)} ${currency}`;
}

export function priceLine(label: string, cents: number, currency: string): string {
  return `${label}: ${formatTicketPrice(cents, currency)}`;
}
