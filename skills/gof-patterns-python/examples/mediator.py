"""Mediator: a chat room routes messages so users never reference each other."""
from __future__ import annotations


class ChatRoom:
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def join(self, user: User) -> None:
        self._users[user.name] = user
        user.room = self

    def send(self, sender: str, text: str, to: str | None = None) -> None:
        targets = [to] if to else [n for n in self._users if n != sender]
        for name in targets:
            self._users[name].receive(sender, text)


class User:
    def __init__(self, name: str) -> None:
        self.name = name
        self.room: ChatRoom | None = None
        self.inbox: list[str] = []

    def say(self, text: str, to: str | None = None) -> None:
        assert self.room is not None
        self.room.send(self.name, text, to)

    def receive(self, sender: str, text: str) -> None:
        self.inbox.append(f"{sender}: {text}")


if __name__ == "__main__":
    room = ChatRoom()
    ana, bo, cy = User("ana"), User("bo"), User("cy")
    for u in (ana, bo, cy):
        room.join(u)
    ana.say("hello all")
    bo.say("psst", to="cy")
    print(bo.inbox, cy.inbox)
