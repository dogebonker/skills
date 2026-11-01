// Singleton: static let is lazy and thread-safe; an actor makes the shared state Sendable-safe.
actor AppConfiguration {
    static let shared = AppConfiguration()

    private var values: [String: String] = ["region": "eu-west"]
    private init() {}

    func value(for key: String) -> String? { values[key] }
    func set(_ value: String, for key: String) { values[key] = value }
}

// Usually better: take the dependency as a parameter so tests can pass a fresh instance.
struct Reporter {
    let config: AppConfiguration

    func report() async -> String {
        "region=\(await config.value(for: "region") ?? "unknown")"
    }
}

await AppConfiguration.shared.set("us-east", for: "region")
print(await Reporter(config: .shared).report())
print(await AppConfiguration.shared.value(for: "missing") ?? "nil")
