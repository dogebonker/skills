"""Visitor: functools.singledispatch adds operations to a fixed set of node types."""
from __future__ import annotations

from dataclasses import dataclass
from functools import singledispatch


@dataclass
class Num:
    value: float


@dataclass
class Add:
    left: "Expr"
    right: "Expr"


@dataclass
class Mul:
    left: "Expr"
    right: "Expr"


Expr = Num | Add | Mul


@singledispatch
def evaluate(node: object) -> float:
    raise TypeError(f"unsupported {type(node).__name__}")


@evaluate.register
def _(node: Num) -> float:
    return node.value


@evaluate.register
def _(node: Add) -> float:
    return evaluate(node.left) + evaluate(node.right)


@evaluate.register
def _(node: Mul) -> float:
    return evaluate(node.left) * evaluate(node.right)


@singledispatch
def render(node: object) -> str:
    raise TypeError(f"unsupported {type(node).__name__}")


@render.register
def _(node: Num) -> str:
    return str(node.value)


@render.register
def _(node: Add) -> str:
    return f"({render(node.left)} + {render(node.right)})"


@render.register
def _(node: Mul) -> str:
    return f"{render(node.left)} * {render(node.right)}"


if __name__ == "__main__":
    tree = Mul(Add(Num(2), Num(3)), Num(4))
    print(render(tree), "=", evaluate(tree))
