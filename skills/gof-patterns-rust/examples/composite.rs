// Composite: a recursive enum. Vec already heap-allocates children, so no Box is needed; match replaces virtual calls.
enum Node {
    File { name: String, size: u64 },
    Dir { name: String, children: Vec<Node> },
}

impl Node {
    fn file(name: &str, size: u64) -> Node {
        Node::File {
            name: name.into(),
            size,
        }
    }
    fn dir(name: &str, children: Vec<Node>) -> Node {
        Node::Dir {
            name: name.into(),
            children,
        }
    }
    fn size(&self) -> u64 {
        match self {
            Node::File { size, .. } => *size,
            Node::Dir { children, .. } => children.iter().map(Node::size).sum(),
        }
    }
    fn print(&self, depth: usize) {
        let pad = "  ".repeat(depth);
        match self {
            Node::File { name, size } => println!("{pad}{name} ({size} B)"),
            Node::Dir { name, children } => {
                println!("{pad}{name}/ ({} B)", self.size());
                children.iter().for_each(|c| c.print(depth + 1));
            }
        }
    }
}

fn main() {
    let root = Node::dir(
        "project",
        vec![
            Node::file("README.md", 1200),
            Node::dir(
                "src",
                vec![Node::file("main.rs", 4000), Node::file("lib.rs", 2500)],
            ),
        ],
    );
    root.print(0);
}
