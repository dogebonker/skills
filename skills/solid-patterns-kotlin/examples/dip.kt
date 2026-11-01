// DIP: the order policy owns the abstraction it needs; the SMS detail plugs in. Same output.

data class Order(val id: String, val phone: String, val totalCents: Long)

// A low-level detail. In an Android app this lives in the data layer.
// Every line the gateway sends, so the demo can compare the two versions.
val smsLog = mutableListOf<String>()

class SmsGateway {
    fun send(phone: String, text: String) {
        val line = "  [sms $phone] $text"
        smsLog += line
        println(line)
    }
}

fun confirmation(order: Order): String = "Order ${order.id} confirmed: %.2f".format(java.util.Locale.ROOT, order.totalCents / 100.0)

// --- Violation: business policy constructs and depends on a concrete transport.
class OrderServiceV1 {
    private val sms = SmsGateway()

    fun place(order: Order): String {
        sms.send(order.phone, confirmation(order))
        return order.id
    }
}

// --- Fix: the policy declares the port it needs and receives an implementation.
// With Hilt: `class OrderService @Inject constructor(private val notifier: OrderNotifier)`,
// plus a @Module with `@Binds abstract fun bind(impl: SmsOrderNotifier): OrderNotifier`.
fun interface OrderNotifier {
    fun orderConfirmed(phone: String, text: String)
}

class OrderService(private val notifier: OrderNotifier) {
    fun place(order: Order): String {
        notifier.orderConfirmed(order.phone, confirmation(order))
        return order.id
    }
}

class SmsOrderNotifier(private val gateway: SmsGateway) : OrderNotifier {
    override fun orderConfirmed(phone: String, text: String) = gateway.send(phone, text)
}

fun main() {
    val order = Order("A-1042", "+351900000000", 3599)
    println("violation:")
    OrderServiceV1().place(order)
    val violationSent = smsLog.toList()
    smsLog.clear()
    // Composition root (on Android, the Hilt graph): the only place that knows the detail.
    println("fix:")
    OrderService(SmsOrderNotifier(SmsGateway())).place(order)
    println("same output: ${violationSent == smsLog}")
    // A test swaps the detail with a lambda; no mocking library needed.
    val sent = mutableListOf<String>()
    OrderService { _, text -> sent += text }.place(order)
    println("fix with fake: $sent")
}
