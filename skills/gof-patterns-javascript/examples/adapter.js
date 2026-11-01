'use strict';

const promisify =
  (fn) =>
  (...args) =>
    new Promise((resolve, reject) => {
      fn(...args, (err, data) => (err ? reject(err) : resolve(data)));
    });

class ArrayToQueueAdapter {
  #array = null;
  #head = 0;

  constructor(array) {
    if (!Array.isArray(array)) {
      throw new Error('Array instance expected');
    }
    this.#array = array;
  }

  enqueue(data) {
    this.#array.push(data);
  }

  // Head index instead of shift(): O(1) amortized, compacts when half is used
  dequeue() {
    if (this.#head === this.#array.length) return undefined;
    const data = this.#array[this.#head++];
    if (this.#head * 2 >= this.#array.length) {
      this.#array.splice(0, this.#head);
      this.#head = 0;
    }
    return data;
  }

  get count() {
    return this.#array.length - this.#head;
  }
}

module.exports = { promisify, ArrayToQueueAdapter };

if (require.main === module) {
  const double = (n, callback) => {
    if (n < 0) callback(new Error('negative'));
    else callback(null, n * 2);
  };
  const doubleAsync = promisify(double);
  doubleAsync(21).then((n) => console.log('promisify:', n));
  doubleAsync(-1).catch((err) => console.log('promisify error:', err.message));

  const queue = new ArrayToQueueAdapter([]);
  for (const item of ['a', 'b', 'c']) queue.enqueue(item);
  console.log(queue.dequeue(), queue.dequeue(), 'count:', queue.count);
  queue.enqueue('d');
  const rest = [queue.dequeue(), queue.dequeue(), queue.dequeue()];
  console.log(rest, 'count:', queue.count);
}
