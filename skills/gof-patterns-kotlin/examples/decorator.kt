// Decorator: class delegation with `by` forwards everything, and we override only what we change.

interface Storage {
    fun save(key: String, value: String)
    fun load(key: String): String?
}

class MemoryStorage : Storage {
    private val data = mutableMapOf<String, String>()
    override fun save(key: String, value: String) { data[key] = value }
    override fun load(key: String): String? = data[key]
}

class LoggingStorage(private val inner: Storage) : Storage by inner {
    override fun save(key: String, value: String) {
        println("save($key)")
        inner.save(key, value)
    }
}

class UppercaseStorage(private val inner: Storage) : Storage by inner {
    override fun save(key: String, value: String) = inner.save(key, value.uppercase())
}

fun main() {
    // Decorators stack: logging wraps uppercase wraps memory.
    val storage: Storage = LoggingStorage(UppercaseStorage(MemoryStorage()))
    storage.save("greeting", "hello")
    println(storage.load("greeting"))   // load is forwarded by `by inner`
}
