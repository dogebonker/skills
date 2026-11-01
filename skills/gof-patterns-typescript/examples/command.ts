export {};

// Command: each edit is a function pair (execute/undo) stored on a history stack.
interface Command {
  execute(): void;
  undo(): void;
}

class TextDocument {
  text = "";
}

const appendText = (doc: TextDocument, added: string): Command => {
  let before = "";
  return {
    execute: () => {
      before = doc.text;
      doc.text += added;
    },
    undo: () => {
      doc.text = before;
    },
  };
};

class Editor {
  readonly #history: Command[] = [];

  run(cmd: Command): void {
    cmd.execute();
    this.#history.push(cmd);
  }

  undo(): void {
    this.#history.pop()?.undo();
  }
}

const doc = new TextDocument();
const editor = new Editor();
editor.run(appendText(doc, "Hello"));
editor.run(appendText(doc, ", world"));
console.log(JSON.stringify(doc.text));
editor.undo();
console.log(JSON.stringify(doc.text));
