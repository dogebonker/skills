"""Singleton: in Python, a module-level instance is the singleton.

In a real project this would live in its own module (settings.py) and callers
would do `from settings import settings`; the import system caches the module,
so every importer shares one object. A Singleton class adds nothing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class Settings:
    debug: bool = False
    tags: list[str] = field(default_factory=list)


settings = Settings()  # the module-level singleton


# When construction is expensive or lazy, cache a factory function instead.
@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings(debug=True)


if __name__ == "__main__":
    settings.tags.append("prod")
    print(settings)
    assert get_settings() is get_settings()
    print(get_settings())
