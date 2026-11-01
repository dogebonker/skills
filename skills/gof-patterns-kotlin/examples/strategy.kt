// Strategy: a function type is the strategy interface, and lambdas are the implementations.

typealias ShippingCost = (weightKg: Double) -> Double

val standard: ShippingCost = { kg -> 4.0 + kg * 0.5 }
val express: ShippingCost = { kg -> 9.0 + kg * 1.2 }
val pickup: ShippingCost = { 0.0 }

class Cart(private val weightKg: Double, private var shipping: ShippingCost = standard) {
    fun choose(strategy: ShippingCost) {
        shipping = strategy
    }

    fun shippingCost(): Double = shipping(weightKg)
}

fun main() {
    val cart = Cart(weightKg = 3.0)
    println("standard: %.2f".format(cart.shippingCost()))
    cart.choose(express)
    println("express: %.2f".format(cart.shippingCost()))
    cart.choose(pickup)
    println("pickup: %.2f".format(cart.shippingCost()))
    cart.choose { kg -> if (kg > 2.0) 1.0 else 2.0 }     // an ad hoc strategy
    println("promo: %.2f".format(cart.shippingCost()))
}
