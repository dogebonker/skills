'use strict';

class Pool {
  #available = [];
  #inUse = new Set();
  #factory = null;
  #reset = null;
  #size = 0;

  constructor(factory, reset, size) {
    this.#factory = factory;
    this.#reset = reset;
    this.#size = size;
    for (let i = 0; i < size; i++) this.#available.push(factory());
  }

  acquire() {
    const obj = this.#available.pop() ?? this.#factory();
    this.#inUse.add(obj);
    return obj;
  }

  // Ignores objects not acquired from this pool and second releases
  release(obj) {
    if (!this.#inUse.delete(obj)) return;
    if (this.#available.length >= this.#size) return;
    this.#reset(obj);
    this.#available.push(obj);
  }
}

module.exports = { Pool };

if (require.main === module) {
  const buffers = new Pool(() => Buffer.alloc(4), (b) => b.fill(0), 2);
  const buffer = buffers.acquire();
  buffers.acquire(); // pool now empty, so a double release would fit under the size cap
  buffer.write('dirt');
  buffers.release(buffer);
  buffers.release(buffer); // ignored: buffer is no longer in use
  const first = buffers.acquire();
  const second = buffers.acquire();
  console.log('reused:', first === buffer, 'reset:', first.toString('hex'));
  console.log('two acquires differ:', first !== second);
}
