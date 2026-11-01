// Iterator: conform to Sequence and IteratorProtocol, then get map/filter/for-in for free.
struct Playlist: Sequence {
    let songs: [String]

    // Iterate newest-first without exposing the storage layout.
    func makeIterator() -> ReverseIterator {
        ReverseIterator(songs: songs, index: songs.count)
    }

    struct ReverseIterator: IteratorProtocol {
        let songs: [String]
        var index: Int

        mutating func next() -> String? {
            guard index > 0 else { return nil }
            index -= 1
            return songs[index]
        }
    }
}

let playlist = Playlist(songs: ["Intro", "Verse", "Chorus", "Outro"])
for song in playlist { print(song) }
print(playlist.filter { $0.count > 5 }.map { $0.uppercased() })

// Lazy infinite sequence with the stdlib helper.
let powers = sequence(first: 1) { $0 * 2 }.prefix(6)
print(Array(powers))
