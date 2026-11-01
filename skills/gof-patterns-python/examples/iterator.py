"""Iterator: generators and __iter__ replace hand-written iterator classes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass
class Page:
    items: list[str]


class Catalog:
    def __init__(self, pages: list[Page]) -> None:
        self._pages = pages

    def __iter__(self) -> Iterator[str]:
        """Flatten pages lazily; callers never see the page structure."""
        for page in self._pages:
            yield from page.items

    def reversed_items(self) -> Iterator[str]:
        for page in reversed(self._pages):
            yield from reversed(page.items)


if __name__ == "__main__":
    catalog = Catalog([Page(["a", "b"]), Page(["c"]), Page(["d", "e"])])
    print(list(catalog))
    print(list(catalog.reversed_items()))
    it = iter(catalog)
    print(next(it), next(it))
