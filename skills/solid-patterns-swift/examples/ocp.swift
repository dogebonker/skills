// OCP in Swift: the tracker depends on a protocol. A new destination is a
// new conforming type, and even an existing type can join through an
// extension (retroactive conformance) without editing its source.

struct Event {
    let name: String
    let screen: String
}

// --- Violation: each destination adds a case and edits this function.
func trackV1(_ event: Event, destinations: [String]) -> [String] {
    destinations.map { destination in
        switch destination {
        case "console": return "console: \(event.name)@\(event.screen)"
        case "warehouse": return "warehouse: {\"event\":\"\(event.name)\"}"
        default: return "unknown destination \(destination)"
        }
    }
}

// --- Fix: Tracker is closed; destinations extend it.
protocol AnalyticsSink {
    func send(_ event: Event) -> String
}

struct ConsoleSink: AnalyticsSink {
    func send(_ event: Event) -> String { "console: \(event.name)@\(event.screen)" }
}

// An existing type we do not edit, from another module.
struct WarehouseClient {
    func upload(json: String) -> String { "warehouse: \(json)" }
}

extension WarehouseClient: AnalyticsSink {
    func send(_ event: Event) -> String { upload(json: "{\"event\":\"\(event.name)\"}") }
}

struct Tracker {
    let sinks: [any AnalyticsSink]
    func track(_ event: Event) -> [String] { sinks.map { $0.send(event) } }
}

let event = Event(name: "checkout_started", screen: "cart")
let before = trackV1(event, destinations: ["console", "warehouse"])
let after = Tracker(sinks: [ConsoleSink(), WarehouseClient()]).track(event)
after.forEach { print($0) }
print("same output: \(before == after)")
