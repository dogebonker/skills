// Adapter: wrap a third-party style API so it satisfies our protocol.
protocol PaymentGateway {
    func charge(cents: Int, currency: String) -> Bool
}

// Existing API we cannot change: takes dollars as a Double and returns a status string.
struct LegacyBillingSDK {
    func submit(amount: Double, code: String) -> String {
        amount > 0 ? "OK:\(code)" : "FAIL"
    }
}

struct LegacyBillingAdapter: PaymentGateway {
    let sdk: LegacyBillingSDK

    func charge(cents: Int, currency: String) -> Bool {
        sdk.submit(amount: Double(cents) / 100, code: currency).hasPrefix("OK")
    }
}

// Alternative for one-off cases: conform the foreign type via an extension.
extension LegacyBillingSDK: PaymentGateway {
    func charge(cents: Int, currency: String) -> Bool {
        submit(amount: Double(cents) / 100, code: currency).hasPrefix("OK")
    }
}

func checkout(using gateway: some PaymentGateway) -> String {
    gateway.charge(cents: 1999, currency: "EUR") ? "paid" : "declined"
}

print(checkout(using: LegacyBillingAdapter(sdk: LegacyBillingSDK())))
print(checkout(using: LegacyBillingSDK()))
