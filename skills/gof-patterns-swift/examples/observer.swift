// Observer: AsyncStream delivers events to any number of independent subscribers.
actor PriceFeed {
    private var continuations: [Int: AsyncStream<Double>.Continuation] = [:]
    private var nextID = 0

    func subscribe() -> AsyncStream<Double> {
        let (stream, continuation) = AsyncStream<Double>.makeStream(bufferingPolicy: .bufferingNewest(16))
        let id = nextID
        nextID += 1
        continuations[id] = continuation
        // A cancelled or dropped subscriber removes itself.
        continuation.onTermination = { [weak self] _ in
            Task { await self?.remove(id) }
        }
        return stream
    }

    private func remove(_ id: Int) { continuations[id] = nil }

    var subscriberCount: Int { continuations.count }

    func publish(_ price: Double) {
        for continuation in continuations.values { continuation.yield(price) }
    }

    func finish() {
        for continuation in continuations.values { continuation.finish() }
        continuations.removeAll()
    }
}

let feed = PriceFeed()
let chartStream = await feed.subscribe()
let alertStream = await feed.subscribe()

// A subscriber that leaves early: cancelling its task terminates its stream.
let tickerStream = await feed.subscribe()
let ticker = Task { for await _ in tickerStream {} }
ticker.cancel()
while await feed.subscriberCount > 2 { await Task.yield() }
print("subscribers after cancel:", await feed.subscriberCount)

async let chart: [String] = {
    var lines: [String] = []
    for await price in chartStream { lines.append("chart: \(price)") }
    return lines
}()
async let alerts: [String] = {
    var lines: [String] = []
    for await price in alertStream where price > 100 { lines.append("alert: \(price)") }
    return lines
}()

for price in [99.5, 101.0, 105.25] { await feed.publish(price) }
await feed.finish()
print(await chart)
print(await alerts)
print("subscribers after finish:", await feed.subscriberCount)
