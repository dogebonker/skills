'use strict';

const fs = require('node:fs');

class PriceApi {
  fetch(sku) {
    console.log(`api: fetch ${sku}`);
    return sku.length * 10;
  }
}

// Composition proxy: holds the target, same interface, adds a cache and stats
class PriceApiProxy {
  #api;
  #cache = new Map();
  #stats = { hits: 0, misses: 0 };

  constructor(api) {
    this.#api = api;
  }

  fetch(sku) {
    if (this.#cache.has(sku)) {
      this.#stats.hits++;
      return this.#cache.get(sku);
    }
    this.#stats.misses++;
    const price = this.#api.fetch(sku);
    this.#cache.set(sku, price);
    return price;
  }

  get stats() {
    return { ...this.#stats };
  }
}

// Subclass proxy for a platform type that callers must receive as-is
const statistics = { bytes: 0, chunks: 0, events: {} };

class StatReadStream extends fs.ReadStream {
  emit(name, ...args) {
    if (name === 'data') {
      // Bytes, not string length: 'é' is one UTF-16 unit but two UTF-8 bytes
      statistics.bytes += Buffer.byteLength(args[0]);
      statistics.chunks++;
    }
    const counter = statistics.events[name] ?? 0;
    statistics.events[name] = counter + 1;
    return super.emit(name, ...args);
  }
}

const getStatistics = () => structuredClone(statistics);

const createReadStream = (path, options) => new StatReadStream(path, options);

module.exports = {
  PriceApi,
  PriceApiProxy,
  StatReadStream,
  createReadStream,
  getStatistics,
};

if (require.main === module) {
  const prices = new PriceApiProxy(new PriceApi());
  console.log(prices.fetch('book'), prices.fetch('book'), prices.fetch('pen'));
  console.log(prices.stats);

  const stream = createReadStream(__filename, { encoding: 'utf8' });
  stream.resume();
  stream.on('close', () => {
    const { bytes, chunks } = getStatistics();
    console.log({ bytes, chunks, fileSize: fs.statSync(__filename).size });
  });
}
