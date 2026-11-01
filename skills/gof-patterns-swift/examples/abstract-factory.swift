// Abstract Factory: one factory yields a matching family of storage products.
protocol Cache { func describe() -> String }
protocol Database { func describe() -> String }

protocol StorageFactory {
    func makeCache() -> any Cache
    func makeDatabase() -> any Database
}

struct InMemoryCache: Cache { func describe() -> String { "dictionary cache" } }
struct InMemoryDatabase: Database { func describe() -> String { "array-backed database" } }
struct RedisLikeCache: Cache { func describe() -> String { "networked cache" } }
struct PostgresLikeDatabase: Database { func describe() -> String { "SQL database" } }

struct LocalStorageFactory: StorageFactory {
    func makeCache() -> any Cache { InMemoryCache() }
    func makeDatabase() -> any Database { InMemoryDatabase() }
}

struct ProductionStorageFactory: StorageFactory {
    func makeCache() -> any Cache { RedisLikeCache() }
    func makeDatabase() -> any Database { PostgresLikeDatabase() }
}

struct OrderService {
    let cache: any Cache
    let database: any Database

    // The client only sees the factory protocol.
    init(factory: any StorageFactory) {
        cache = factory.makeCache()
        database = factory.makeDatabase()
    }

    func summary() -> String { "\(cache.describe()) + \(database.describe())" }
}

for factory in [LocalStorageFactory() as any StorageFactory, ProductionStorageFactory()] {
    print(OrderService(factory: factory).summary())
}
