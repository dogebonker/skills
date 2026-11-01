export {};

// Visitor: a discriminated union with an exhaustive switch adds new operations without touching the node types.
type Expr =
  | { kind: "num"; value: number }
  | { kind: "add"; left: Expr; right: Expr }
  | { kind: "mul"; left: Expr; right: Expr };

function evaluate(e: Expr): number {
  switch (e.kind) {
    case "num":
      return e.value;
    case "add":
      return evaluate(e.left) + evaluate(e.right);
    case "mul":
      return evaluate(e.left) * evaluate(e.right);
    default: {
      const unreachable: never = e;
      return unreachable;
    }
  }
}

function show(e: Expr): string {
  switch (e.kind) {
    case "num":
      return String(e.value);
    case "add":
      return `(${show(e.left)} + ${show(e.right)})`;
    case "mul":
      return `${show(e.left)} * ${show(e.right)}`;
    default: {
      const unreachable: never = e;
      return unreachable;
    }
  }
}

const expr: Expr = {
  kind: "mul",
  left: { kind: "add", left: { kind: "num", value: 2 }, right: { kind: "num", value: 3 } },
  right: { kind: "num", value: 4 },
};
console.log(show(expr), "=", evaluate(expr));
