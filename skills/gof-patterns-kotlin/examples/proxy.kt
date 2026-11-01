// Proxy: CachingWeather implements the same interface and delegates what it does not change with `by`.

interface Weather {
    fun forecast(city: String): String
    fun units(): String
}

class RemoteWeather : Weather {
    override fun forecast(city: String): String {
        println("network call for $city")
        return "$city: 21C sunny"
    }

    override fun units() = "celsius"
}

class CachingWeather(private val real: Weather) : Weather by real {
    private val cache = mutableMapOf<String, String>()

    override fun forecast(city: String): String =
        cache.getOrPut(city) { real.forecast(city) }
}

fun main() {
    val weather: Weather = CachingWeather(RemoteWeather())
    println(weather.forecast("Porto"))
    println(weather.forecast("Porto"))   // served from cache, no network line
    println(weather.units())
    // For a lazily created real object, a property `val real by lazy { RemoteWeather() }` does the same job.
}
