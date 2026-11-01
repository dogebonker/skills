package main

import "fmt"

// ChatRoom is the mediator: users never reference each other.
type ChatRoom struct{ members map[string]*User }

func NewChatRoom() *ChatRoom { return &ChatRoom{members: map[string]*User{}} }

func (c *ChatRoom) Join(u *User) {
	c.members[u.name] = u
	u.room = c
}

func (c *ChatRoom) Broadcast(from, msg string) {
	for name, u := range c.members {
		if name != from {
			u.Receive(from, msg)
		}
	}
}

type User struct {
	name string
	room *ChatRoom
	got  []string
}

func (u *User) Say(msg string) { u.room.Broadcast(u.name, msg) }
func (u *User) Receive(from, msg string) {
	u.got = append(u.got, from+": "+msg)
}

func main() {
	room := NewChatRoom()
	ann, bob, cy := &User{name: "ann"}, &User{name: "bob"}, &User{name: "cy"}
	for _, u := range []*User{ann, bob, cy} {
		room.Join(u)
	}
	ann.Say("standup in 5")
	bob.Say("on my way")
	fmt.Println("cy sees:", cy.got)
	fmt.Println("ann sees:", ann.got)
}
