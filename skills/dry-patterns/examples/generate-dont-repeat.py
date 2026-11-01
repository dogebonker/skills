"""Generate, don't repeat: field names were typed three times per resource.
The fix keeps one spec and generates the code from it."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- Violation: hand-written model, parser and serializer repeat each field ---
@dataclass
class InvoiceV1:
    invoice_id: str
    customer_id: str
    total_cents: int


def invoice_from_json_v1(data: dict[str, Any]) -> InvoiceV1:
    return InvoiceV1(
        invoice_id=str(data["invoiceId"]),
        customer_id=str(data["customerId"]),
        total_cents=int(data["totalCents"]),
    )


def invoice_to_json_v1(inv: InvoiceV1) -> dict[str, Any]:
    return {"invoiceId": inv.invoice_id, "customerId": inv.customer_id, "totalCents": inv.total_cents}


# --- Fix: one spec; a build step renders source from it ---
SPEC = {"Invoice": [("invoice_id", "invoiceId", "str"), ("customer_id", "customerId", "str"), ("total_cents", "totalCents", "int")]}


def generate(spec: dict[str, list[tuple[str, str, str]]]) -> str:
    out = ["# Generated from SPEC. Edit the spec and regenerate.", "from dataclasses import dataclass", ""]
    for name, fields in spec.items():
        out += ["@dataclass", f"class {name}:"] + [f"    {py}: {typ}" for py, _, typ in fields] + [""]
        out += ["    @classmethod", "    def from_json(cls, data):", "        return cls("]
        out += [f"            {py}={typ}(data[{js!r}])," for py, js, typ in fields] + ["        )", ""]
        out += ["    def to_json(self):", "        return {"]
        out += [f"            {js!r}: self.{py}," for py, js, _ in fields] + ["        }", ""]
    return "\n".join(out)


if __name__ == "__main__":
    # A real build writes this to invoice_model.py and commits it; exec keeps the demo in one file.
    source = generate(SPEC)
    namespace: dict[str, Any] = {}
    exec(compile(source, "<generated>", "exec"), namespace)
    Invoice = namespace["Invoice"]

    payload = {"invoiceId": "INV-1042", "customerId": "C-7", "totalCents": "4500"}
    before = invoice_to_json_v1(invoice_from_json_v1(payload))
    after = Invoice.from_json(payload).to_json()
    print(after, "same" if before == after else "DIFFERENT")
    print(f"generated {len(source.splitlines())} lines from {len(SPEC['Invoice'])} spec rows")
