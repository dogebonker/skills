export {};

// Memento: the editor exports an opaque readonly snapshot; the caretaker stores it without reading it.
declare const snapshotBrand: unique symbol;
type Snapshot = { readonly [snapshotBrand]: true };

class FormEditor {
  #fields: Record<string, string> = {};

  set(name: string, value: string): void {
    this.#fields[name] = value;
  }

  save(): Snapshot {
    return Object.freeze({ ...this.#fields }) as unknown as Snapshot;
  }

  restore(s?: Snapshot): void {
    if (!s) return;
    this.#fields = { ...(s as unknown as Record<string, string>) };
  }

  toString(): string {
    return JSON.stringify(this.#fields);
  }
}

const form = new FormEditor();
const snapshots: Snapshot[] = [];

form.set("email", "a@example.com");
snapshots.push(form.save());
form.set("email", "typo@");
form.set("plan", "pro");
console.log("current:", String(form));

form.restore(snapshots.pop());
console.log("restored:", String(form));
form.restore(snapshots.pop());
console.log("undo past empty:", String(form));
