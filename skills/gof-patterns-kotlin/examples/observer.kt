// Observer: subscribers are lambdas, and subscribing returns a function that unsubscribes.
// On Android, StateFlow collected in a lifecycle scope is the standard version of this.

import kotlin.properties.Delegates

class Thermostat {
    private val listeners = mutableListOf<(Int) -> Unit>()

    fun observe(listener: (Int) -> Unit): () -> Unit {
        val entry: (Int) -> Unit = { listener(it) }   // own wrapper, so removing it never removes another subscription
        listeners += entry
        return { listeners.remove(entry) }
    }

    var temperature: Int by Delegates.observable(20) { _, old, new ->
        if (old != new) listeners.toList().forEach { it(new) }
    }
}

fun main() {
    val thermostat = Thermostat()
    val stopDisplay = thermostat.observe { println("display: $it C") }
    thermostat.observe { if (it > 25) println("alarm: too hot ($it C)") }

    thermostat.temperature = 22
    thermostat.temperature = 27
    stopDisplay()
    thermostat.temperature = 18   // only the alarm listener remains
}
