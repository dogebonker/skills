// Flyweight: a factory hands out shared immutable MapIcon objects, and each marker keeps only its own position.

class MapIcon(val name: String, private val pixels: ByteArray) {   // heavy, shared; pixels stay private so nobody mutates them
    val byteCount: Int get() = pixels.size
}

object IconFactory {
    private val cache = HashMap<String, MapIcon>()

    fun get(name: String): MapIcon = cache.getOrPut(name) {
        println("loading icon $name")
        MapIcon(name, ByteArray(1024))
    }

    fun cachedCount(): Int = cache.size
}

class Marker(val x: Int, val y: Int, val icon: MapIcon)   // extrinsic state: x and y

fun main() {
    val markers = (1..6).map { i ->
        Marker(x = i * 10, y = i * 5, icon = IconFactory.get(if (i % 2 == 0) "cafe" else "bank"))
    }
    println("markers = ${markers.size}, icons loaded = ${IconFactory.cachedCount()}")
    println("shared = ${markers[0].icon === markers[2].icon}, bytes per icon = ${markers[0].icon.byteCount}")
}
