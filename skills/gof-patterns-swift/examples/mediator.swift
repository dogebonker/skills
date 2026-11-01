// Mediator: an actor coordinates chat participants so they never reference each other.
actor ChatRoom {
    private var inboxes: [String: [String]] = [:]

    func join(_ name: String) {
        if inboxes[name] == nil { inboxes[name] = [] }
    }

    func send(from sender: String, text: String) {
        let line = "\(sender): \(text)"
        for name in Array(inboxes.keys) where name != sender {
            inboxes[name, default: []].append(line)
        }
    }

    func inbox(of name: String) -> [String] { inboxes[name] ?? [] }
}

struct Participant: Sendable {
    let name: String
    let room: ChatRoom

    func say(_ text: String) async { await room.send(from: name, text: text) }
}

let room = ChatRoom()
let alice = Participant(name: "alice", room: room)
let bob = Participant(name: "bob", room: room)
await room.join("alice")
await room.join("bob")
await alice.say("hi bob")
await room.join("bob")  // rejoining keeps bob's inbox
await bob.say("hi alice")
print(await room.inbox(of: "alice"))
print(await room.inbox(of: "bob"))
