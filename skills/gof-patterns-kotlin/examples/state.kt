// State: (Kotlin 1.9+ for `data object`) a sealed interface lists the states and an exhaustive `when` defines the transitions.

sealed interface OrderState {
    data object Created : OrderState
    data class Shipped(val tracking: String) : OrderState
    data object Delivered : OrderState
    data object Cancelled : OrderState
}

enum class Event { PAY_AND_SHIP, DELIVER, CANCEL }

fun OrderState.on(event: Event): OrderState = when (this) {
    OrderState.Created -> when (event) {
        Event.PAY_AND_SHIP -> OrderState.Shipped("TRACK-42")
        Event.CANCEL -> OrderState.Cancelled
        Event.DELIVER -> this
    }
    is OrderState.Shipped -> when (event) {
        Event.DELIVER -> OrderState.Delivered
        Event.PAY_AND_SHIP, Event.CANCEL -> this   // cannot cancel after shipping
    }
    OrderState.Delivered -> this
    OrderState.Cancelled -> this
}

fun main() {
    var state: OrderState = OrderState.Created
    for (event in listOf(Event.DELIVER, Event.PAY_AND_SHIP, Event.CANCEL, Event.DELIVER)) {
        state = state.on(event)
        println("$event -> $state")
    }
}
