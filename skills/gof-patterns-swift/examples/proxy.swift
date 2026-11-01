// Proxy: a lazy, caching stand-in with the same interface as the real image loader.
protocol ImageLoader {
    func load(_ name: String) -> String
}

struct DiskImageLoader: ImageLoader {
    func load(_ name: String) -> String {
        print("  (slow disk read of \(name))")
        return "pixels:\(name)"
    }
}

// A class holds the cache, so the protocol method stays non-mutating.
// Use an actor instead when the proxy is shared across tasks.
final class CachingImageProxy<Real: ImageLoader>: ImageLoader {
    private let real: Real
    private var cache: [String: String] = [:]

    init(real: Real) { self.real = real }

    func load(_ name: String) -> String {
        if let hit = cache[name] { return hit }
        let result = real.load(name)
        cache[name] = result
        return result
    }
}

let loader: any ImageLoader = CachingImageProxy(real: DiskImageLoader())
print(loader.load("cat.png"))
print(loader.load("cat.png"))
print(loader.load("dog.png"))
