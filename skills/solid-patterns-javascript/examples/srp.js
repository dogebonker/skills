'use strict';

// SRP: one module per reason to change. Both versions print the same invoice.

// --- Violation: tax maths (finance), layout (product) and storage (ops) share one class.
class InvoiceServiceV1 {
  #saved = new Map();

  issue(id, lines, vatRate) {
    const net = lines.reduce((sum, l) => sum + l.qty * l.unitCents, 0);
    const total = Math.round(net * (1 + vatRate));
    const text = [...lines.map((l) => `${l.sku} x${l.qty}`), `TOTAL ${(total / 100).toFixed(2)}`].join('\n');
    this.#saved.set(id, text);
    return text;
  }
}

// --- Fix: one function per reason to change; storage is its own small object.
const invoiceTotalCents = (lines, vatRate) => {
  const net = lines.reduce((sum, l) => sum + l.qty * l.unitCents, 0);
  return Math.round(net * (1 + vatRate));
};

const renderInvoice = (lines, totalCents) =>
  [...lines.map((l) => `${l.sku} x${l.qty}`), `TOTAL ${(totalCents / 100).toFixed(2)}`].join('\n');

const createInvoiceArchive = () => {
  const saved = new Map();
  return { save: (id, text) => saved.set(id, text), size: () => saved.size };
};

const issueInvoice = (id, lines, vatRate, archive) => {
  const text = renderInvoice(lines, invoiceTotalCents(lines, vatRate));
  archive.save(id, text);
  return text;
};

module.exports = { InvoiceServiceV1, invoiceTotalCents, renderInvoice, createInvoiceArchive, issueInvoice };

if (require.main === module) {
  const lines = [
    { sku: 'KB-101', qty: 2, unitCents: 4999 },
    { sku: 'MS-220', qty: 1, unitCents: 2450 },
  ];
  const before = new InvoiceServiceV1().issue('INV-1', lines, 0.2);
  const archive = createInvoiceArchive();
  const after = issueInvoice('INV-1', lines, 0.2, archive);
  console.log(`violation:\n${before}`);
  console.log(`fix:\n${after}`);
  console.log('same output:', before === after, '| archived:', archive.size());
}
