// Mediator: participants talk only to the ChatRoom, never to each other.

interface Room {
    fun broadcast(from: User, text: String)
}

class User(val name: String, private val room: Room) {
    fun say(text: String) = room.broadcast(this, text)
    fun receive(from: User, text: String) = println("$name got from ${from.name}: $text")
}

class ChatRoom : Room {
    private val members = mutableListOf<User>()

    fun join(name: String): User = User(name, this).also { members += it }

    override fun broadcast(from: User, text: String) {
        for (member in members) {
            if (member !== from) member.receive(from, text)
        }
    }
}

fun main() {
    val room = ChatRoom()
    val ana = room.join("ana")
    room.join("ben")
    room.join("cris")
    ana.say("meeting at 10")
}
