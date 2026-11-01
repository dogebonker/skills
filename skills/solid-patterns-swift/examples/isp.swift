// ISP in Swift: small protocols, composed with `&` where a caller needs
// more than one. The standard library does this: Codable is Encodable & Decodable.

struct Episode {
    let title: String
}

// --- Violation: one wide protocol. A preview clip cannot download or cast,
// so it ships stubs that crash if anyone calls them.
protocol MediaPlayerV1 {
    func play(_ episode: Episode) -> String
    func download(_ episode: Episode) -> String
    func cast(_ episode: Episode, to device: String) -> String
}

struct PreviewPlayerV1: MediaPlayerV1 {
    func play(_ episode: Episode) -> String { "playing 30s of \(episode.title)" }
    func download(_ episode: Episode) -> String { fatalError("previews cannot be downloaded") }
    func cast(_ episode: Episode, to device: String) -> String { fatalError("previews cannot be cast") }
}

func autoplayV1(_ player: some MediaPlayerV1, queue: [Episode]) -> [String] {
    queue.map { player.play($0) }
}

// --- Fix: one protocol per capability.
protocol Playable {
    func play(_ episode: Episode) -> String
}
protocol Downloadable {
    func download(_ episode: Episode) -> String
}
protocol Castable {
    func cast(_ episode: Episode, to device: String) -> String
}
typealias FullPlayer = Playable & Downloadable & Castable

struct PreviewPlayer: Playable {
    func play(_ episode: Episode) -> String { "playing 30s of \(episode.title)" }
}

struct SubscriberPlayer: FullPlayer {
    func play(_ episode: Episode) -> String { "playing \(episode.title)" }
    func download(_ episode: Episode) -> String { "saved \(episode.title)" }
    func cast(_ episode: Episode, to device: String) -> String { "casting \(episode.title) to \(device)" }
}

func autoplay(_ player: some Playable, queue: [Episode]) -> [String] {
    queue.map { player.play($0) }
}

// A caller that needs two capabilities names both.
func prepareCommute(_ player: some Playable & Downloadable, _ episode: Episode) -> [String] {
    [player.download(episode), player.play(episode)]
}

let queue = [Episode(title: "Swift 6 migration"), Episode(title: "Value types")]
let before = autoplayV1(PreviewPlayerV1(), queue: queue)
let after = autoplay(PreviewPlayer(), queue: queue)
print(after)
print("same output: \(before == after)")
print(prepareCommute(SubscriberPlayer(), queue[0]))
