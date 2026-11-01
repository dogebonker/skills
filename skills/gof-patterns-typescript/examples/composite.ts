export {};

// Composite: files and folders share one interface so a total size works on any node.
interface FsNode {
  readonly name: string;
  size(): number;
  print(indent?: string): string[];
}

class FileNode implements FsNode {
  readonly name: string;
  readonly #bytes: number;

  constructor(name: string, bytes: number) {
    this.name = name;
    this.#bytes = bytes;
  }
  size(): number {
    return this.#bytes;
  }
  print(indent = ""): string[] {
    return [`${indent}${this.name} (${this.#bytes}b)`];
  }
}

class FolderNode implements FsNode {
  readonly name: string;
  private readonly children: FsNode[] = [];

  constructor(name: string) {
    this.name = name;
  }

  add(...nodes: FsNode[]): this {
    this.children.push(...nodes);
    return this;
  }
  size(): number {
    return this.children.reduce((sum, c) => sum + c.size(), 0);
  }
  print(indent = ""): string[] {
    return [`${indent}${this.name}/ (${this.size()}b)`, ...this.children.flatMap((c) => c.print(indent + "  "))];
  }
}

const root = new FolderNode("project").add(
  new FileNode("README.md", 1200),
  new FolderNode("src").add(new FileNode("main.ts", 4000), new FileNode("util.ts", 800)),
);
console.log(root.print().join("\n"));
