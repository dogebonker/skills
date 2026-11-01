# Iterator

Gives sequential access to a collection without exposing its structure; in JavaScript this is the iteration protocol, usually written as a generator.

Refs: https://github.com/HowProgrammingWorks/Iterator  
Example: [examples/iterator.js](../examples/iterator.js)

**Intent** — Traverse the elements of an aggregate one by one while hiding how they are stored.

**Problem** — Callers need several traversal orders or lazy and endless sequences, and should not depend on the internal array, tree or database cursor.

**Applicability** — **Use** `Symbol.iterator` on your own collections and generators for custom orders. **Avoid** a hand-written iterator class with `hasNext()` and `next()` when a generator can yield the items: the generator is enough.

**JS implementation** — Define `*[Symbol.iterator]()` so `for...of`, spread, `Array.from` and destructuring work (`Playlist`). Extra traversals are extra generator methods (`shuffled`, a lazy Fisher-Yates shuffle). Endless sequences are generators with `while (true)` (`cycle`) and need a consumer that stops. Use `async *[Symbol.asyncIterator]` with `for await` for streams and pages. Gotcha: generators are single-use, so `cycle` copies its input into an array first; looping over an exhausted generator would spin forever without yielding, and an empty input returns at once.

**Consequences** — Lazy, memory-friendly traversal behind a standard interface; mutating the collection during iteration gives surprising results.

**Related patterns** — **Composite** for the trees an iterator walks; **Visitor** runs an operation over each node; **Memento** saves the position.
