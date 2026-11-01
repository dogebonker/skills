export {};

// Mediator: participants talk only to the ChatRoom, never to each other.
interface Participant {
  readonly name: string;
  receive(from: string, text: string): void;
}

class ChatRoom {
  readonly #members = new Set<Participant>();

  join(p: Participant): void {
    this.#members.add(p);
    this.broadcast("system", `${p.name} joined`, p);
  }

  broadcast(from: string, text: string, except?: Participant): void {
    for (const m of this.#members) {
      if (m !== except) m.receive(from, text);
    }
  }
}

class User implements Participant {
  readonly name: string;
  readonly #room: ChatRoom;

  constructor(name: string, room: ChatRoom) {
    this.name = name;
    this.#room = room;
  }

  say(text: string): void {
    this.#room.broadcast(this.name, text, this);
  }

  receive(from: string, text: string): void {
    console.log(`[${this.name}] ${from}: ${text}`);
  }
}

const room = new ChatRoom();
const ana = new User("ana", room);
const ben = new User("ben", room);
room.join(ana);
room.join(ben);
ana.say("deploy is green");
ben.say("shipping it");
