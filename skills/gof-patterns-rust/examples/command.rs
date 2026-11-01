// Command: a pair of boxed closures (do, undo) is a command; a Vec is the undo history.
struct Command {
    label: &'static str,
    run: Box<dyn Fn(&mut Vec<String>)>,
    undo: Box<dyn Fn(&mut Vec<String>)>,
}

fn append_line(text: &'static str) -> Command {
    Command {
        label: "append",
        run: Box::new(move |doc| doc.push(text.to_string())),
        undo: Box::new(|doc| {
            doc.pop();
        }),
    }
}

#[derive(Default)]
struct Editor {
    doc: Vec<String>,
    history: Vec<Command>,
}

impl Editor {
    fn execute(&mut self, cmd: Command) {
        (cmd.run)(&mut self.doc);
        self.history.push(cmd);
    }
    fn undo(&mut self) {
        if let Some(cmd) = self.history.pop() {
            (cmd.undo)(&mut self.doc);
            println!("undid {}", cmd.label);
        }
    }
}

fn main() {
    let mut ed = Editor::default();
    ed.execute(append_line("first"));
    ed.execute(append_line("second"));
    println!("{:?}", ed.doc);
    ed.undo();
    println!("{:?}", ed.doc);
}
