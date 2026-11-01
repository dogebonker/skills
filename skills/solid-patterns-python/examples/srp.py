"""SRP: one module per reason to change. Both versions print the same invoice."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    sku: str
    qty: int
    unit_cents: int


# --- Violation: tax maths (finance), layout (product) and storage (ops) share one class.
class InvoiceServiceV1:
    def __init__(self) -> None:
        self._saved: dict[str, str] = {}

    def issue(self, invoice_id: str, lines: list[Line], vat_rate: float) -> str:
        net = sum(line.qty * line.unit_cents for line in lines)
        total = round(net * (1 + vat_rate))
        text = "\n".join([*(f"{l.sku} x{l.qty}" for l in lines), f"TOTAL {total / 100:.2f}"])
        self._saved[invoice_id] = text
        return text


# --- Fix: one function per reason to change; storage is its own small class.
def invoice_total_cents(lines: list[Line], vat_rate: float) -> int:
    net = sum(line.qty * line.unit_cents for line in lines)
    return round(net * (1 + vat_rate))


def render_invoice(lines: list[Line], total_cents: int) -> str:
    return "\n".join([*(f"{l.sku} x{l.qty}" for l in lines), f"TOTAL {total_cents / 100:.2f}"])


class InvoiceArchive:
    def __init__(self) -> None:
        self._saved: dict[str, str] = {}

    def save(self, invoice_id: str, text: str) -> None:
        self._saved[invoice_id] = text

    def __len__(self) -> int:
        return len(self._saved)


def issue_invoice(invoice_id: str, lines: list[Line], vat_rate: float, archive: InvoiceArchive) -> str:
    text = render_invoice(lines, invoice_total_cents(lines, vat_rate))
    archive.save(invoice_id, text)
    return text


if __name__ == "__main__":
    lines = [Line("KB-101", 2, 4999), Line("MS-220", 1, 2450)]
    before = InvoiceServiceV1().issue("INV-1", lines, 0.2)
    archive = InvoiceArchive()
    after = issue_invoice("INV-1", lines, 0.2, archive)
    print(f"violation:\n{before}")
    print(f"fix:\n{after}")
    print("same output:", before == after, "| archived:", len(archive))
