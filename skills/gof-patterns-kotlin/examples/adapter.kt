// Adapter: an extension function wraps a vendor SDK type behind the interface the app expects.

interface MessageSender {
    fun send(phone: String, text: String): Boolean
}

// Pretend this is a third-party class we cannot change.
class LegacySmsGateway {
    fun dispatch(number: String, body: ByteArray): Int {
        println("gateway -> $number: ${body.decodeToString()}")
        return 0
    }
}

fun LegacySmsGateway.asSender(): MessageSender = object : MessageSender {
    override fun send(phone: String, text: String): Boolean {
        // A digit string keeps leading zeros that a Long would drop.
        val number = phone.filter(Char::isDigit).takeIf { it.isNotEmpty() } ?: return false
        return dispatch(number, text.encodeToByteArray()) == 0
    }
}

fun notifyUser(sender: MessageSender, phone: String) {
    val ok = sender.send(phone, "Your code is 1234")
    println("sent=$ok")
}

fun main() {
    val sender = LegacySmsGateway().asSender()
    notifyUser(sender, "+351 912 345 678")
    notifyUser(sender, "0044 20 7946 0000")
    notifyUser(sender, "n/a")
}
