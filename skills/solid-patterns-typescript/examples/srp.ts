export {};

// SRP: one module per reason to change. Both versions print the same invoice.

type Line = { sku: string; qty: number; unitCents: number };

// --- Violation: tax maths (finance), layout (product) and storage (ops) share one class.
class InvoiceServiceV1 {
  readonly #saved = new Map<string, string>();

  issue(id: string, lines: readonly Line[], vatRate: number): string {
    const net = lines.reduce((sum, l) => sum + l.qty * l.unitCents, 0);
    const total = Math.round(net * (1 + vatRate));
    const text = [...lines.map((l) => `${l.sku} x${l.qty}`), `TOTAL ${(total / 100).toFixed(2)}`].join("\n");
    this.#saved.set(id, text);
    return text;
  }
}

// --- Fix: one function or class per reason to change; a thin function composes them.
function invoiceTotalCents(lines: readonly Line[], vatRate: number): number {
  const net = lines.reduce((sum, l) => sum + l.qty * l.unitCents, 0);
  return Math.round(net * (1 + vatRate));
}

function renderInvoice(lines: readonly Line[], totalCents: number): string {
  return [...lines.map((l) => `${l.sku} x${l.qty}`), `TOTAL ${(totalCents / 100).toFixed(2)}`].join("\n");
}

class InvoiceArchive {
  readonly #saved = new Map<string, string>();

  save(id: string, text: string): void {
    this.#saved.set(id, text);
  }

  get size(): number {
    return this.#saved.size;
  }
}

function issueInvoice(id: string, lines: readonly Line[], vatRate: number, archive: InvoiceArchive): string {
  const text = renderInvoice(lines, invoiceTotalCents(lines, vatRate));
  archive.save(id, text);
  return text;
}

const lines: Line[] = [
  { sku: "KB-101", qty: 2, unitCents: 4999 },
  { sku: "MS-220", qty: 1, unitCents: 2450 },
];
const before = new InvoiceServiceV1().issue("INV-1", lines, 0.2);
const archive = new InvoiceArchive();
const after = issueInvoice("INV-1", lines, 0.2, archive);
console.log(`violation:\n${before}`);
console.log(`fix:\n${after}`);
console.log("same output:", before === after, "| archived:", archive.size);
