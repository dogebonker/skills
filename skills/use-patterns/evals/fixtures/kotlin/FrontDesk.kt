package hotel

class LegacyFxService {
    private val quotes = mapOf("EURUSD" to "1.0850", "EURGBP" to "0.8560", "EURCHF" to "0.9410")
    fun quote(pair: String): String = quotes[pair] ?: "1.0000"
}

class Folio(val booking: Booking, private val fx: LegacyFxService) {
    val charges = mutableListOf<Pair<String, Double>>()
    val usedVouchers = mutableSetOf<String>()
    var checkoutHour = 11
    fun balanceEur(): Double = booking.total() + charges.sumOf { it.second }
    fun balanceIn(currency: String): Double = balanceEur() * fx.quote("EUR$currency").toDouble()
    fun depositIn(currency: String): Double = booking.nightlyRate * fx.quote("EUR" + currency).toDouble()
    fun chargeIn(currency: String, index: Int): Double = charges[index].second * fx.quote("EUR$currency").toDouble()
}

class FrontDesk(private val folio: Folio) {
    private val done = ArrayDeque<List<String>>()
    fun handle(request: String) {
        val parts = request.split(" ")
        when (parts[0]) {
            "minibar" -> folio.charges.add("Minibar" to parts[1].toDouble())
            "parking" -> folio.charges.add("Parking ${parts[1]} days" to 15.0 * parts[1].toInt())
            "late-checkout" -> {
                folio.checkoutHour = 14
                folio.charges.add("Late checkout" to 40.0)
            }
            "voucher" -> {
                require(folio.usedVouchers.add(parts[1])) { "voucher ${parts[1]} already used" }
                folio.charges.add("Voucher ${parts[1]}" to -parts[2].toDouble())
            }
            else -> error("unknown request ${parts[0]}")
        }
        done.addLast(parts)
    }

    fun undoLast() {
        val parts = done.removeLast()
        when (parts[0]) {
            "minibar", "parking" -> folio.charges.removeLast()
            "late-checkout" -> {
                folio.checkoutHour = 11
                folio.charges.removeLast()
            }
            "voucher" -> {
                folio.usedVouchers.remove(parts[1])
                folio.charges.removeLast()
            }
        }
    }
}

class PdfInvoice(private val folio: Folio) {
    fun render(): String = buildString {
        appendLine("%PDF-1.4 INVOICE ${folio.booking.id}")
        appendLine("Guest: ${folio.booking.guest}")
        folio.charges.forEach { (label, amount) -> appendLine("$label  $amount") }
        appendLine("Total EUR ${"%.2f".format(folio.balanceEur())}")
        appendLine("%%EOF")
    }
}

class EmailInvoice(private val folio: Folio) {
    fun render(): String = buildString {
        appendLine("Subject: Your invoice ${folio.booking.id}")
        appendLine("Dear ${folio.booking.guest},")
        folio.charges.forEach { (label, amount) -> appendLine("- $label: $amount") }
        appendLine("Total: EUR ${"%.2f".format(folio.balanceEur())}")
        appendLine("Kind regards, Hotel Lisboa")
    }
}

class SmsInvoice(private val folio: Folio) {
    fun render(): String = buildString {
        appendLine("INV ${folio.booking.id}")
        appendLine(folio.booking.guest)
        folio.charges.forEach { (label, amount) -> appendLine("$label $amount") }
        appendLine("EUR ${"%.2f".format(folio.balanceEur())}")
        appendLine("Reply STOP to opt out")
    }
}

fun main() {
    val booking = Booking("B-7", "Ana Silva", RoomType.DOUBLE, 3, 120.0)
    booking.confirm()
    booking.checkIn()
    val folio = Folio(booking, LegacyFxService())
    val desk = FrontDesk(folio)
    listOf("minibar 12.5", "parking 2", "late-checkout", "voucher WELCOME 20").forEach(desk::handle)
    desk.undoLast()
    println(PdfInvoice(folio).render() + EmailInvoice(folio).render() + SmsInvoice(folio).render())
    println("%.2f %.2f %.2f".format(folio.balanceIn("USD"), folio.depositIn("GBP"), folio.chargeIn("CHF", 0)))
    println("${capacity(booking.room)} ${nightlyPrice(120.0, true)} ${booking.refundable()}")
    runExtras(booking)
}

interface Notifier {
    fun send(guest: String, text: String): String
}

class EmailNotifier(private val from: String) : Notifier {
    override fun send(guest: String, text: String): String = "mail $from -> $guest: $text"
}

class SmsNotifier(private val senderId: String) : Notifier {
    override fun send(guest: String, text: String): String = "sms $senderId -> $guest: ${text.take(160)}"
}

fun notifyGuest(notifiers: List<Notifier>, guest: String, text: String): List<String> = notifiers.map { it.send(guest, text) }

fun runExtras(booking: Booking) {
    println("${cancellationFee(booking, 24)} ${canCancelFree(72)} ${reminderDelaySeconds()} $MAX_GUESTS_PER_BOOKING $LOYALTY_POINTS_PER_NIGHT")
    val rooms = upgradeAll(listOf(Room("101", 120.0), StaffRoom("S1")), Room("501", 300.0))
    println(rooms.map { it.number } + occupancyReport(listOf(booking)))
    println(DateSpan(3, 7).intersect(DateSpan(5, 9)).toString() + " " + DateSpan(1, 4).shift(2).extend(1).nights())
    println(notifyGuest(listOf(EmailNotifier("desk@hotel.test"), SmsNotifier("HOTEL")), booking.guest, "Welcome"))
}
