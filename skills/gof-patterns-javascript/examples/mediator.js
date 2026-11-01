'use strict';

// Participants know only the mediator, never each other
class ChatRoom {
  #users = new Map();

  join(name, onMessage) {
    this.#users.set(name, onMessage);
    return (text) => this.#broadcast(name, text);
  }

  #broadcast(from, text) {
    for (const [name, onMessage] of this.#users) {
      if (name !== from) onMessage(from, text);
    }
  }
}

module.exports = { ChatRoom };

if (require.main === module) {
  const room = new ChatRoom();
  const say = room.join('alice', (from, text) => console.log(`alice <- ${from}: ${text}`));
  room.join('bob', (from, text) => console.log(`bob <- ${from}: ${text}`));
  room.join('carol', () => {});
  say('hi all');
}
