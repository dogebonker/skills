// State: an enum holds the states, and a switch in one place defines every transition.
enum OrderState {
    case pending
    case paid(receipt: String)
    case shipped(tracking: String)
    case cancelled

    enum Event {
        case pay(receipt: String)
        case ship(tracking: String)
        case cancel
    }

    func handling(_ event: Event) -> OrderState {
        switch (self, event) {
        case (.pending, .pay(let receipt)):
            return .paid(receipt: receipt)
        case (.paid, .ship(let tracking)):
            return .shipped(tracking: tracking)
        case (.pending, .cancel), (.paid, .cancel):
            return .cancelled
        case (.pending, .ship), (.paid, .pay), (.shipped, _), (.cancelled, _):
            return self // illegal events are ignored, listed explicitly so a new case fails to compile
        }
    }
}

var order = OrderState.pending
order = order.handling(.ship(tracking: "T1")) // ignored: not paid yet
print(order)
order = order.handling(.pay(receipt: "R9"))
print(order)
order = order.handling(.ship(tracking: "T1"))
print(order)
order = order.handling(.cancel) // ignored: already shipped
print(order)
