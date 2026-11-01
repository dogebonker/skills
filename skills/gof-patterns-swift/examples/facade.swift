// Facade: one small entry point hides several subsystems.
final class Inventory {
    private var reserved: Set<String> = []

    func reserve(sku: String) -> Bool {
        guard sku != "OUT-OF-STOCK" else { return false }
        reserved.insert(sku)
        return true
    }

    func release(sku: String) {
        reserved.remove(sku)
        print("released \(sku)")
    }
}

struct Payments {
    struct Charge { let id: String; let cents: Int }

    func charge(cents: Int) -> Charge? {
        cents < 100_000 ? Charge(id: "ch-\(cents)", cents: cents) : nil
    }
}

struct Shipping {
    func schedule(sku: String, quantity: Int) -> String { "shipment-for-\(quantity)x\(sku)" }
}

struct OrderFacade {
    private let inventory = Inventory()
    private let payments = Payments()
    private let shipping = Shipping()

    enum Failure: Error { case invalidInput, unavailable, paymentDeclined }

    func placeOrder(sku: String, quantity: Int, cents: Int) throws -> (shipment: String, charge: Payments.Charge) {
        guard quantity > 0, cents >= 0 else { throw Failure.invalidInput }
        guard inventory.reserve(sku: sku) else { throw Failure.unavailable }
        guard let charge = payments.charge(cents: cents) else {
            inventory.release(sku: sku)  // compensate the committed reservation
            throw Failure.paymentDeclined
        }
        return (shipping.schedule(sku: sku, quantity: quantity), charge)
    }
}

let facade = OrderFacade()
for (sku, quantity, cents) in [("BOOK-1", 1, 2500), ("BOOK-1", 0, 2500), ("OUT-OF-STOCK", 1, 100), ("TV-9", 1, 500_000)] {
    do {
        let order = try facade.placeOrder(sku: sku, quantity: quantity, cents: cents)
        print(order.shipment, "charge:", order.charge.id)
    } catch {
        print("failed:", error)
    }
}
