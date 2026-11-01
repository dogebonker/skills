// Strategy: a function value is the strategy; no class hierarchy needed.
typealias ShippingCost = (_ weightKg: Double) -> Double

let standard: ShippingCost = { 4.0 + $0 * 0.5 }
let express: ShippingCost = { 12.0 + $0 * 1.2 }
let pickup: ShippingCost = { _ in 0 }

struct Checkout {
    var shipping: ShippingCost

    func total(items: Double, weightKg: Double) -> Double {
        items + shipping(weightKg)
    }
}

var checkout = Checkout(shipping: standard)
print(checkout.total(items: 50, weightKg: 4))
checkout.shipping = express
print(checkout.total(items: 50, weightKg: 4))
checkout.shipping = pickup
print(checkout.total(items: 50, weightKg: 4))

// The stdlib uses the same idea: sorted(by:) takes a comparison strategy.
print(["pear", "fig", "banana"].sorted { $0.count < $1.count })
