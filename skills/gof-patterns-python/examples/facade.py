"""Facade: one simple call hides several subsystem steps."""
from __future__ import annotations


class Inventory:
    def reserve(self, sku: str, qty: int) -> bool:
        return qty <= 5

    def release(self, sku: str, qty: int) -> None:
        print(f"released {sku}")


class Payments:
    def charge(self, customer: str, cents: int) -> str:
        if customer == "mallory":
            raise RuntimeError("card declined")
        return f"pay-{customer}-{cents}"


class Shipping:
    def schedule(self, customer: str, sku: str) -> str:
        return f"ship-{sku}-to-{customer}"


class OrderFacade:
    def __init__(self) -> None:
        self._inv, self._pay, self._ship = Inventory(), Payments(), Shipping()

    def place_order(self, customer: str, sku: str, qty: int, cents: int) -> str:
        if qty <= 0 or cents < 0:
            raise ValueError("qty must be > 0 and cents >= 0")
        if not self._inv.reserve(sku, qty):
            return "out of stock"
        try:
            receipt = self._pay.charge(customer, cents * qty)
        except Exception:
            self._inv.release(sku, qty)
            raise
        return f"{receipt}, {self._ship.schedule(customer, sku)}"


if __name__ == "__main__":
    shop = OrderFacade()
    print(shop.place_order("ana", "A1", 2, 500))
    print(shop.place_order("ana", "A1", 50, 500))
    try:
        shop.place_order("mallory", "A1", 1, 500)
    except RuntimeError as e:
        print("failed:", e)
    try:
        shop.place_order("ana", "A1", 0, 500)
    except ValueError as e:
        print("failed:", e)
