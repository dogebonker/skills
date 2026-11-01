// Bridge: notification kinds (abstraction) vary independently from delivery channels (implementation).
protocol Channel {
    func deliver(_ text: String) -> String
}

struct EmailChannel: Channel {
    func deliver(_ text: String) -> String { "email<\(text)>" }
}

struct SMSChannel: Channel {
    func deliver(_ text: String) -> String { "sms<\(text.prefix(20))>" }
}

protocol Notification {
    var channel: any Channel { get }
    var message: String { get }
}

extension Notification {
    func send() -> String { channel.deliver(message) }
}

struct Alert: Notification {
    let channel: any Channel
    let reason: String
    var message: String { "ALERT: \(reason)" }
}

struct Receipt: Notification {
    let channel: any Channel
    let orderID: Int
    var message: String { "Receipt for order #\(orderID)" }
}

let channels: [any Channel] = [EmailChannel(), SMSChannel()]
for channel in channels {
    print(Alert(channel: channel, reason: "disk almost full").send())
    print(Receipt(channel: channel, orderID: 7).send())
}
