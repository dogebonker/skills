// Singleton: an object declaration is initialised lazily and exactly once; the JVM makes that initialisation thread-safe.
// Its mutable state is not thread-safe by itself, so callLog is guarded with @Synchronized and bounded.
// On Android prefer a DI container (Hilt @Singleton) so tests can swap it.

object PaymentConfig {
    private const val MAX_LOG = 3
    private val callLog = ArrayDeque<String>()

    init {
        println("PaymentConfig initialised")
    }

    @Synchronized
    fun record(call: String) {
        if (callLog.size == MAX_LOG) callLog.removeFirst()
        callLog.addLast(call)
    }

    @Synchronized
    fun history(): List<String> = callLog.toList()
}

// DI-friendly alternative: a plain class, with one instance created and passed by the app.
class Clock(private val now: () -> Long = System::currentTimeMillis) {
    fun millis(): Long = now()
}

fun main() {
    println("start")
    PaymentConfig.record("charge 10")      // first access runs init
    PaymentConfig.record("refund 5")
    PaymentConfig.record("charge 7")
    PaymentConfig.record("charge 3")       // the log keeps only the newest MAX_LOG entries
    println(PaymentConfig.history())
    println(PaymentConfig === PaymentConfig)

    val workers = List(4) { n -> Thread { repeat(100) { PaymentConfig.record("worker $n") } } }
    workers.forEach { it.start() }
    workers.forEach { it.join() }
    println("entries after concurrent writes = ${PaymentConfig.history().size}")

    val fixedClock = Clock { 42L }          // easy to fake, which a global object is not
    println(fixedClock.millis())
}
