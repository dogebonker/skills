'use strict';

class Document {
  #state = { title: '', body: '' };

  edit(changes) {
    Object.assign(this.#state, changes);
  }

  // Memento is an opaque, immutable snapshot
  save() {
    return Object.freeze(structuredClone(this.#state));
  }

  restore(memento) {
    if (!memento) return;
    this.#state = structuredClone(memento);
  }

  get view() {
    return { ...this.#state };
  }
}

// Caretaker stores snapshots and never looks inside
class History {
  #stack = [];

  push(memento) {
    this.#stack.push(memento);
  }

  pop() {
    return this.#stack.pop();
  }
}

module.exports = { Document, History };

if (require.main === module) {
  const doc = new Document();
  const history = new History();
  doc.edit({ title: 'Draft' });
  history.push(doc.save());
  doc.edit({ title: 'Final', body: 'Done' });
  console.log(doc.view);
  doc.restore(history.pop());
  console.log(doc.view);
  doc.restore(history.pop());
  console.log('undo on empty history:', doc.view);
}
