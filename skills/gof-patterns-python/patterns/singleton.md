# Singleton

In Python, a module-level instance is the singleton: imports are cached, so every importer shares one object.

Refs: https://refactoring.guru/design-patterns/singleton/python/example
Example: [examples/singleton.py](../examples/singleton.py)

**Intent** — Guarantee one instance of a thing and give it a global access point.

**Problem** — Configuration, a connection pool or a registry must be shared, not duplicated.

**Applicability** — **Use** when exactly one shared instance is a real requirement. **Avoid** a Singleton class with `__new__` or a metaclass: a module-level instance (`settings = Settings()` in `settings.py`, imported with `from settings import settings`) is simpler, testable and idiomatic. For lazy or expensive creation, use a function decorated with `functools.lru_cache`.

**Python implementation** — The example defines `settings` at module level and `get_settings()` cached with `lru_cache`, whose repeated calls return the same object. Gotchas: running a file as `__main__` and also importing it creates two module objects, so keep the singleton in a separate module; global state hampers tests, so accept the instance as a parameter in functions and override it in tests; `lru_cache` does not lock, so two threads can each build an instance on the first call: create it eagerly at import, or guard creation with a `threading.Lock`.

**Consequences** — Trivial to write and shared by default. Cost: hidden global dependency and test coupling.

**Related patterns** — **Abstract Factory** and **Facade** objects are often held as module-level singletons; **Flyweight** shares many objects rather than one.
