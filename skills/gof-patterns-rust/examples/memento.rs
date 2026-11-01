// Memento: the snapshot type lives in a module with a private field, so only Editor can read it.
mod editor {
    pub struct Snapshot {
        text: String,
        cursor: usize,
    }

    #[derive(Default)]
    pub struct Editor {
        text: String,
        cursor: usize,
    }

    impl Editor {
        pub fn type_text(&mut self, s: &str) {
            self.text.push_str(s);
            self.cursor = self.text.len();
        }
        pub fn save(&self) -> Snapshot {
            Snapshot {
                text: self.text.clone(),
                cursor: self.cursor,
            }
        }
        // Takes the snapshot by value: a memento is restored once.
        pub fn restore(&mut self, snap: Snapshot) {
            self.text = snap.text;
            self.cursor = snap.cursor;
        }
        pub fn view(&self) -> String {
            format!("{:?} @{}", self.text, self.cursor)
        }
    }
}

use editor::Editor;

fn main() {
    let mut ed = Editor::default();
    let mut history = Vec::new();

    ed.type_text("hello");
    history.push(ed.save());
    ed.type_text(", world");
    println!("now:  {}", ed.view());

    if let Some(snap) = history.pop() {
        ed.restore(snap);
    }
    println!("back: {}", ed.view());
}
