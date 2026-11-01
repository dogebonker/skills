// Factory Method: each subclass of AlertService decides which Notifier to create.

interface Notifier {
    fun send(to: String, text: String): String
}

class EmailNotifier : Notifier {
    override fun send(to: String, text: String) = "email to $to: $text"
}

class PushNotifier : Notifier {
    override fun send(to: String, text: String) = "push to $to: $text"
}

abstract class AlertService {
    // The factory method. Subclasses choose the product.
    protected abstract fun createNotifier(): Notifier

    fun alert(user: String, text: String): String =
        createNotifier().send(user, "ALERT $text")
}

class EmailAlertService : AlertService() {
    override fun createNotifier(): Notifier = EmailNotifier()
}

class PushAlertService : AlertService() {
    override fun createNotifier(): Notifier = PushNotifier()
}

// Often enough in Kotlin: pass the factory as a function instead of subclassing.
class LambdaAlertService(private val create: () -> Notifier) {
    fun alert(user: String, text: String): String = create().send(user, "ALERT $text")
}

fun main() {
    for (service in listOf(EmailAlertService(), PushAlertService())) {
        println(service.alert("ana", "disk full"))
    }
    println(LambdaAlertService(::PushNotifier).alert("ben", "low battery"))
}
