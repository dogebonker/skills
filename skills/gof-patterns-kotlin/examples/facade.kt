// Facade: CheckoutFacade offers one call over three subsystems.

class Inventory {
    fun reserve(sku: String, qty: Int): Boolean {
        println("inventory: reserved $qty x $sku")
        return true
    }

    fun release(sku: String) {
        println("released $sku")
    }
}

data class Charge(val id: String, val cents: Long)

class PaymentGateway(private val limitCents: Long = 10_000) {
    fun charge(customer: String, cents: Long): Charge? {
        if (cents > limitCents) {
            println("payment: declined $customer $cents cents")
            return null
        }
        println("payment: charged $customer $cents cents")
        return Charge("CH-$customer-$cents", cents)
    }
}

class Shipping {
    fun schedule(customer: String, sku: String): String {
        println("shipping: scheduled $sku for $customer")
        return "TRACK-001"
    }
}

data class Order(val tracking: String, val charge: Charge)

class CheckoutFacade(
    private val inventory: Inventory = Inventory(),
    private val payments: PaymentGateway = PaymentGateway(),
    private val shipping: Shipping = Shipping(),
) {
    fun buy(customer: String, sku: String, qty: Int, priceCents: Long): Order? {
        require(qty > 0) { "qty must be positive, was $qty" }
        require(priceCents >= 0) { "priceCents must not be negative, was $priceCents" }
        if (!inventory.reserve(sku, qty)) return null
        val charge = payments.charge(customer, priceCents * qty) ?: run {
            inventory.release(sku)   // compensate the committed reservation
            return null
        }
        return Order(shipping.schedule(customer, sku), charge)
    }
}

fun main() {
    val checkout = CheckoutFacade()
    println("order = ${checkout.buy("ana", "SKU-9", 2, 1_500)}")
    println("order = ${checkout.buy("ben", "SKU-7", 1, 50_000)}")
    try {
        checkout.buy("ana", "SKU-9", 0, 1_500)
    } catch (e: IllegalArgumentException) {
        println("rejected: ${e.message}")
    }
}
