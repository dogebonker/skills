"""Rule of three: tolerate a second copy, extract on the third."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    name: str
    street: str
    postcode: str
    city: str
    country: str


# --- Violation: the third copy arrived and was pasted again ---
def invoice_header_v1(a: Address) -> str:
    return f"{a.name}\n{a.street}\n{a.postcode} {a.city.upper()}\n{a.country.upper()}"


def shipping_label_v1(a: Address) -> str:
    return f"{a.name}\n{a.street}\n{a.postcode} {a.city.upper()}\n{a.country.upper()}"


def packing_slip_v1(a: Address, order_id: int) -> str:
    return f"Order {order_id}\n{a.name}\n{a.street}\n{a.postcode} {a.city.upper()}\n{a.country.upper()}"


# --- Fix: three real callers show what is shared; extract exactly that ---
def postal_block(a: Address) -> str:
    return f"{a.name}\n{a.street}\n{a.postcode} {a.city.upper()}\n{a.country.upper()}"


def invoice_header(a: Address) -> str:
    return postal_block(a)


def shipping_label(a: Address) -> str:
    return postal_block(a)


def packing_slip(a: Address, order_id: int) -> str:
    return f"Order {order_id}\n{postal_block(a)}"


if __name__ == "__main__":
    addr = Address("Ana Silva", "Rua Augusta 12", "1100-053", "Lisboa", "Portugal")
    pairs = [
        ("invoice", invoice_header_v1(addr), invoice_header(addr)),
        ("label", shipping_label_v1(addr), shipping_label(addr)),
        ("slip", packing_slip_v1(addr, 1042), packing_slip(addr, 1042)),
    ]
    for name, before, after in pairs:
        print(name, after.replace("\n", " | "), "same" if before == after else "DIFFERENT")
