export {};

// Observer: a typed event emitter; subscribers are plain functions and subscribe() returns an unsubscribe.
type Listener<T> = (event: T) => void;

class Emitter<T> {
  readonly #listeners = new Set<Listener<T>>();

  subscribe(fn: Listener<T>): () => void {
    this.#listeners.add(fn);
    return () => this.#listeners.delete(fn);
  }

  emit(event: T): void {
    for (const fn of [...this.#listeners]) fn(event);
  }
}

interface PriceChange {
  readonly symbol: string;
  readonly price: number;
}

const ticker = new Emitter<PriceChange>();
const stopLogging = ticker.subscribe((e) => console.log(`log: ${e.symbol} = ${e.price}`));
ticker.subscribe((e) => {
  if (e.price > 100) console.log(`alert: ${e.symbol} above 100`);
});

ticker.emit({ symbol: "ACME", price: 98 });
stopLogging();
ticker.emit({ symbol: "ACME", price: 104 });
