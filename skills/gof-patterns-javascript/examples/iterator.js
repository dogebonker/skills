'use strict';

class Playlist {
  #tracks = [];

  add(title) {
    this.#tracks.push(title);
    return this;
  }

  // Symbol.iterator makes for...of, spread and destructuring work
  *[Symbol.iterator]() {
    yield* this.#tracks;
  }

  // Alternative traversal as a separate generator
  // Lazy Fisher-Yates: each step swaps a random remaining track into place
  *shuffled(random = Math.random) {
    const copy = [...this.#tracks];
    for (let i = copy.length - 1; i >= 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
      yield copy[i];
    }
  }
}

// Infinite sequence; buffers first so one-shot iterators repeat too
function* cycle(items) {
  const buf = [...items];
  if (!buf.length) return;
  while (true) yield* buf;
}

module.exports = { Playlist, cycle };

if (require.main === module) {
  const playlist = new Playlist().add('Intro').add('Verse').add('Outro');
  console.log([...playlist]);
  console.log([...playlist.shuffled(() => 0)]);
  const loop = cycle(playlist.shuffled(() => 0));
  console.log(Array.from({ length: 5 }, () => loop.next().value));
  console.log([...cycle([])]);
}
