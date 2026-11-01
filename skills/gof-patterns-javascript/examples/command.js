'use strict';

// Command: a closure pair (execute, undo) that is a plain object
const createCommand = (execute, undo) => ({ execute, undo });

class Editor {
  text = '';
  #history = [];

  run(command) {
    command.execute();
    this.#history.push(command);
  }

  undo() {
    const command = this.#history.pop();
    if (command) command.undo();
  }
}

const append = (editor, str) => {
  let before = '';
  return createCommand(
    () => {
      before = editor.text;
      editor.text += str;
    },
    () => {
      editor.text = before;
    },
  );
};

module.exports = { createCommand, Editor, append };

if (require.main === module) {
  const editor = new Editor();
  editor.run(append(editor, 'Hello'));
  editor.run(append(editor, ', world'));
  console.log(editor.text);
  editor.undo();
  console.log(editor.text);
}
