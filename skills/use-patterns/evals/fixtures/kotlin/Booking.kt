package hotel

enum class RoomType { SINGLE, DOUBLE, SUITE }
enum class BookingStatus { REQUESTED, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED }

object TaxSettings { var cityTaxPerNight = 2.0 }

fun capacity(type: RoomType): Int = when (type) {
    RoomType.SINGLE -> 1
    RoomType.DOUBLE -> 2
    RoomType.SUITE -> 4
}

fun nightlyPrice(base: Double, weekend: Boolean): Double = if (weekend) base * 1.2 else base

class Booking(val id: String, val guest: String, val room: RoomType, val nights: Int, val nightlyRate: Double) {
    var status = BookingStatus.REQUESTED
        private set

    fun confirm() {
        when (status) {
            BookingStatus.REQUESTED -> status = BookingStatus.CONFIRMED
            BookingStatus.CONFIRMED -> {}
            else -> error("cannot confirm a booking that is $status")
        }
    }

    fun checkIn() {
        when (status) {
            BookingStatus.CONFIRMED -> status = BookingStatus.CHECKED_IN
            BookingStatus.REQUESTED -> error("booking $id is not confirmed yet")
            else -> error("cannot check in a booking that is $status")
        }
    }

    fun checkOut() {
        if (status != BookingStatus.CHECKED_IN) error("guest is not checked in")
        status = BookingStatus.CHECKED_OUT
    }

    fun cancel() {
        when (status) {
            BookingStatus.REQUESTED, BookingStatus.CONFIRMED -> status = BookingStatus.CANCELLED
            BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT -> error("stay already started")
            BookingStatus.CANCELLED -> {}
        }
    }

    fun refundable(): Boolean = when (status) {
        BookingStatus.REQUESTED, BookingStatus.CONFIRMED -> true
        else -> false
    }

    fun total(): Double = nights * nightlyRate + nights * TaxSettings.cityTaxPerNight
}

fun cancellationFee(booking: Booking, hoursBeforeArrival: Int): Double =
    if (hoursBeforeArrival < 48) booking.nightlyRate else 0.0

fun canCancelFree(hoursBeforeArrival: Int): Boolean = hoursBeforeArrival >= 48

fun reminderDelaySeconds(): Long = 172800

const val MAX_GUESTS_PER_BOOKING = 8
const val LOYALTY_POINTS_PER_NIGHT = 8

open class Room(val number: String, val rate: Double) {
    open fun upgradeTo(other: Room): Room = other
    open fun nightlyCharge(nights: Int): Double = rate * nights
}

class StaffRoom(number: String) : Room(number, 0.0) {
    override fun upgradeTo(other: Room): Room = throw UnsupportedOperationException("staff rooms cannot be upgraded")
}

fun upgradeAll(rooms: List<Room>, target: Room): List<Room> = rooms.map { if (it is StaffRoom) it else it.upgradeTo(target) }

fun occupancyReport(bookings: List<Booking>, format: String = "text", locale: String = "pt-PT", onLine: ((String) -> Unit)? = null): String =
    bookings.joinToString("\n") { "${it.id} ${it.status} ${it.nights}" }

class DateSpan(val startDay: Int, val endDay: Int) {
    init { require(endDay >= startDay) { "end before start" } }
    fun nights(): Int = endDay - startDay
    fun contains(day: Int): Boolean = day in startDay until endDay
    fun overlaps(o: DateSpan): Boolean = startDay < o.endDay && o.startDay < endDay
    fun intersect(o: DateSpan): DateSpan? = if (overlaps(o)) DateSpan(maxOf(startDay, o.startDay), minOf(endDay, o.endDay)) else null
    fun shift(days: Int): DateSpan = DateSpan(startDay + days, endDay + days)
    fun extend(days: Int): DateSpan = DateSpan(startDay, endDay + days)
    override fun toString(): String = "day $startDay to day $endDay"
}
