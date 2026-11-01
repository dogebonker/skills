// Mediator: participants never reference each other. They hold an id; the room owns them all,
// so no Rc<RefCell<..>> back-references are needed.
struct User {
    name: String,
    inbox: Vec<String>,
}

#[derive(Default)]
struct ChatRoom {
    users: Vec<User>,
}

impl ChatRoom {
    fn join(&mut self, name: &str) -> usize {
        self.users.push(User {
            name: name.into(),
            inbox: Vec::new(),
        });
        self.users.len() - 1
    }

    // The mediator routes: sender is excluded, everyone else gets the message.
    fn say(&mut self, from: usize, text: &str) {
        let line = format!("{}: {text}", self.users[from].name);
        for (id, user) in self.users.iter_mut().enumerate() {
            if id != from {
                user.inbox.push(line.clone());
            }
        }
    }
}

fn main() {
    let mut room = ChatRoom::default();
    let ana = room.join("ana");
    let bo = room.join("bo");
    let _cy = room.join("cy");

    room.say(ana, "standup now?");
    room.say(bo, "joining");

    for u in &room.users {
        println!("{} inbox: {:?}", u.name, u.inbox);
    }
}
