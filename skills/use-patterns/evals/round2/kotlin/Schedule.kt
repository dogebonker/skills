package gym

import gym.billing.MemberRate
import gym.billing.PriceRule
import gym.billing.invoiceLine

data class GymClass(val id: String, val title: String, val mode: String, val capacity: Int, val day: Int, val hour: Int)

data class Booking(val classId: String, val memberId: String, val member: Boolean, val exercises: List<String>)

data class TimetableUiState(val rows: List<String>, val warnings: List<String>, val revenueCents: Long)

const val DROP_IN_CENTS = 1200L
const val WAITLIST_LIMIT = 5
const val LOW_TURNOUT_SHARE = 0.3
const val MAX_CLASSES_PER_WEEK = 6
const val STREAM_BASE_URL = "https://live.example-gym.test"

val LEGACY_DROP_IN_PRICES = mapOf("spin" to 900L, "yoga" to 800L, "boxing" to 1100L)

class DropInRate(private val surchargeCents: Long) : PriceRule {
    override fun price(baseCents: Long): Long = baseCents + surchargeCents
}

fun parsePayload(json: Map<String, Any?>): Booking? {
    val classId = json["class_id"] as? String ?: return null
    val memberId = (json["member"] as? Map<*, *>)?.get("id") as? String ?: return null
    val member = json["membership"] is String
    val exercises = (json["plan"] as? List<*>)?.filterIsInstance<String>().orEmpty()
    return Booking(classId, memberId, member, exercises)
}

fun formatEuros(cents: Long): String = "EUR %d.%02d".format(cents / 100, cents % 100)

fun spotsPerHour(classes: List<GymClass>, hour: Int): Int = classes.filter { it.hour == hour }.sumOf { it.capacity }

fun waitlistEta(classes: List<GymClass>, hour: Int, position: Int): Int = position / maxOf(1, spotsPerHour(classes, hour))

fun peakHourShare(classes: List<GymClass>, hour: Int): Double =
    spotsPerHour(classes, hour).toDouble() / maxOf(1, classes.sumOf { it.capacity })

fun legacyDropInPrice(title: String): Long = LEGACY_DROP_IN_PRICES[title.lowercase()] ?: DROP_IN_CENTS

fun isVirtual(gymClass: GymClass): Boolean = gymClass.mode.trim().lowercase() == "virtual"

fun buildTimetableState(classes: List<GymClass>, bookings: List<Booking>, rules: Map<Boolean, PriceRule>): TimetableUiState {
    val warnings = mutableListOf<String>()
    val classById = classes.associateBy { it.id }
    val valid = mutableListOf<Booking>()
    for (booking in bookings) {
        if (booking.classId !in classById) {
            warnings += "booking for unknown class ${booking.classId}"
            continue
        }
        if (valid.any { it.classId == booking.classId && it.memberId == booking.memberId }) {
            warnings += "duplicate booking by ${booking.memberId}"
            continue
        }
        valid += booking
    }

    val attendees = valid.groupBy { it.classId }
    val waitlists = mutableMapOf<String, Int>()
    for (gymClass in classes) {
        val booked = attendees[gymClass.id].orEmpty().size
        if (isVirtual(gymClass)) continue
        if (booked > gymClass.capacity) {
            waitlists[gymClass.id] = minOf(booked - gymClass.capacity, WAITLIST_LIMIT)
        }
    }

    var revenueCents = 0L
    for (booking in valid) {
        val gymClass = classById.getValue(booking.classId)
        if (gymClass.mode == "virtual") continue
        val rule = rules.getValue(booking.member)
        revenueCents += rule.price(DROP_IN_CENTS)
    }

    val names = exerciseNames()
    for (booking in valid) {
        val unknown = booking.exercises.filter { it !in names }
        if (unknown.isNotEmpty()) warnings += "${booking.memberId} planned unknown exercises: ${unknown.joinToString()}"
    }
    val popular = valid.flatMap { it.exercises }
        .groupingBy { it }
        .eachCount()
        .entries
        .sortedByDescending { it.value }
        .take(3)
        .map { "${names[it.key] ?: it.key} (${it.value})" }

    val rows = mutableListOf<String>()
    for (gymClass in classes.sortedWith(compareBy({ it.day }, { it.hour }))) {
        val booked = attendees[gymClass.id].orEmpty().size
        val label = if (isVirtual(gymClass)) "online" else "$booked/${gymClass.capacity}"
        val waiting = waitlists[gymClass.id]?.let { ", $it waiting" }.orEmpty()
        rows += "Day ${gymClass.day} ${gymClass.hour}:00 ${gymClass.title} [$label$waiting]"
        val share = booked.toDouble() / gymClass.capacity
        if (share < LOW_TURNOUT_SHARE) warnings += "${gymClass.title} on day ${gymClass.day} is under-booked"
    }
    rows += invoiceLine("Expected class revenue", revenueCents)
    if (popular.isNotEmpty()) rows += "Most planned: ${popular.joinToString()}"

    val perDay = valid.groupingBy { classById.getValue(it.classId).day }.eachCount()
    for ((day, count) in perDay.toSortedMap()) {
        rows += "Day $day: $count bookings"
    }

    val perMember = valid.groupingBy { it.memberId }.eachCount()
    for ((memberId, count) in perMember) {
        if (count > MAX_CLASSES_PER_WEEK) warnings += "$memberId booked $count classes this week"
    }
    val members = valid.count { it.member }
    rows += "Bookings: ${valid.size} ($members by members, ${valid.size - members} drop-in)"
    rows += "Active members this week: ${perMember.size}"
    rows += "Waitlisted: ${waitlists.values.sum()}"

    val inPerson = classes.filterNot(::isVirtual)
    val seats = inPerson.sumOf { it.capacity }
    val taken = inPerson.sumOf { minOf(attendees[it.id].orEmpty().size, it.capacity) }
    rows += "Studio occupancy: $taken of $seats seats"
    val streams = classes.filter(::isVirtual).map { "${it.title}: $STREAM_BASE_URL/${it.id}" }
    if (streams.isNotEmpty()) rows += "Streams: ${streams.joinToString("; ")}"
    return TimetableUiState(rows, warnings, revenueCents)
}

fun exerciseNames(): Map<String, String> = mapOf(
    "back_squat" to "Back squat",
    "front_squat" to "Front squat",
    "goblet_squat" to "Goblet squat",
    "split_squat" to "Bulgarian split squat",
    "lunge" to "Walking lunge",
    "step_up" to "Step-up",
    "deadlift" to "Conventional deadlift",
    "sumo_deadlift" to "Sumo deadlift",
    "romanian_deadlift" to "Romanian deadlift",
    "hip_thrust" to "Barbell hip thrust",
    "glute_bridge" to "Glute bridge",
    "leg_press" to "Leg press",
    "leg_extension" to "Leg extension",
    "leg_curl" to "Lying leg curl",
    "calf_raise" to "Standing calf raise",
    "seated_calf" to "Seated calf raise",
    "bench_press" to "Flat bench press",
    "incline_press" to "Incline bench press",
    "decline_press" to "Decline bench press",
    "dumbbell_press" to "Dumbbell bench press",
    "chest_fly" to "Dumbbell chest fly",
    "cable_crossover" to "Cable crossover",
    "push_up" to "Push-up",
    "dip" to "Parallel bar dip",
    "overhead_press" to "Standing overhead press",
    "arnold_press" to "Arnold press",
    "lateral_raise" to "Lateral raise",
    "front_raise" to "Front raise",
    "rear_delt_fly" to "Rear delt fly",
    "upright_row" to "Upright row",
    "shrug" to "Barbell shrug",
    "pull_up" to "Pull-up",
    "chin_up" to "Chin-up",
    "lat_pulldown" to "Lat pulldown",
    "barbell_row" to "Bent-over barbell row",
    "dumbbell_row" to "One-arm dumbbell row",
    "seated_row" to "Seated cable row",
    "t_bar_row" to "T-bar row",
    "face_pull" to "Face pull",
    "pullover" to "Dumbbell pullover",
    "biceps_curl" to "Barbell biceps curl",
    "hammer_curl" to "Hammer curl",
    "preacher_curl" to "Preacher curl",
    "concentration_curl" to "Concentration curl",
    "triceps_pushdown" to "Triceps pushdown",
    "skull_crusher" to "Skull crusher",
    "overhead_extension" to "Overhead triceps extension",
    "close_grip_press" to "Close-grip bench press",
    "plank" to "Front plank",
    "side_plank" to "Side plank",
    "crunch" to "Crunch",
    "bicycle_crunch" to "Bicycle crunch",
    "leg_raise" to "Hanging leg raise",
    "russian_twist" to "Russian twist",
    "ab_wheel" to "Ab wheel rollout",
    "dead_bug" to "Dead bug",
    "bird_dog" to "Bird dog",
    "mountain_climber" to "Mountain climber",
    "burpee" to "Burpee",
    "box_jump" to "Box jump",
    "jump_squat" to "Jump squat",
    "kettlebell_swing" to "Kettlebell swing",
    "turkish_getup" to "Turkish get-up",
    "clean" to "Power clean",
    "snatch" to "Power snatch",
    "thruster" to "Thruster",
    "wall_ball" to "Wall ball",
    "farmer_carry" to "Farmer's carry",
    "sled_push" to "Sled push",
    "battle_rope" to "Battle ropes",
    "rowing" to "Indoor rowing",
    "assault_bike" to "Air bike",
    "treadmill" to "Treadmill run",
    "stair_climber" to "Stair climber",
    "elliptical" to "Elliptical trainer",
    "jump_rope" to "Jump rope",
    "cycling" to "Indoor cycling",
    "good_morning" to "Good morning",
    "back_extension" to "Back extension",
    "hip_abduction" to "Hip abduction machine",
)

fun main() {
    val classes = listOf(
        GymClass("C1", "Spin", "studio", 2, 1, 7),
        GymClass("C2", "Yoga", " Virtual", 20, 1, 19),
        GymClass("C3", "Boxing", "virtual", 30, 2, 18),
    )
    val payloads = listOf(
        mapOf("class_id" to "C1", "member" to mapOf("id" to "M1"), "membership" to "gold", "plan" to listOf("burpee", "rowing")),
        mapOf("class_id" to "C1", "member" to mapOf("id" to "M2"), "plan" to listOf("rowing")),
        mapOf("class_id" to "C1", "member" to mapOf("id" to "M3"), "membership" to "basic"),
        mapOf("class_id" to "C2", "member" to mapOf("id" to "M1"), "membership" to "gold"),
    )
    val uiState = buildTimetableState(classes, payloads.mapNotNull(::parsePayload), mapOf(true to MemberRate(20), false to DropInRate(300)))
    println((uiState.rows + uiState.warnings).joinToString("\n"))
}
