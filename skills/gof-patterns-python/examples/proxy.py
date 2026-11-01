"""Proxy: a stand-in with the same interface that lazily loads and guards access."""
from __future__ import annotations

from typing import Protocol


class Image(Protocol):
    def render(self) -> str: ...


class HighResImage:
    def __init__(self, path: str) -> None:
        print(f"loading {path} (expensive)")
        self.path = path

    def render(self) -> str:
        return f"pixels of {self.path}"


class LazyImageProxy:
    def __init__(self, path: str, allowed: bool = True) -> None:
        self._path, self._allowed = path, allowed
        self._real: HighResImage | None = None

    def render(self) -> str:
        if not self._allowed:
            raise PermissionError(self._path)
        if self._real is None:
            self._real = HighResImage(self._path)
        return self._real.render()


if __name__ == "__main__":
    img = LazyImageProxy("cat.png")
    print("created, nothing loaded yet")
    print(img.render())
    print(img.render())
    try:
        LazyImageProxy("secret.png", allowed=False).render()
    except PermissionError as e:
        print("denied", e)
