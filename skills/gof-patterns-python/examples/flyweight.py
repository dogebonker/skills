"""Flyweight: share immutable intrinsic state (style) across many glyphs."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Style:
    """Intrinsic, shared, hashable."""

    font: str
    size: int
    bold: bool


_STYLES: dict[Style, Style] = {}


def get_style(font: str, size: int, bold: bool = False) -> Style:
    # Key on the value, not on how the call was written: get_style("Mono", 12) and
    # get_style("Mono", 12, bold=False) must return the same object
    style = Style(font, size, bold)
    return _STYLES.setdefault(style, style)


@dataclass(slots=True)
class Glyph:
    char: str
    x: int  # extrinsic state stays per-instance
    style: Style


if __name__ == "__main__":
    text = "hello"
    glyphs = [Glyph(c, i * 8, get_style("Mono", 12)) for i, c in enumerate(text)]
    print(len({id(g.style) for g in glyphs}), "style object for", len(glyphs), "glyphs")
    print(get_style("Mono", 12) is get_style("Mono", 12, bold=False))
