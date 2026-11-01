export {};

// Iterator: implement [Symbol.iterator] with a generator so for...of works on a custom collection.
interface Page<T> {
  items: T[];
  next?: number;
}

class PagedOrders implements Iterable<string> {
  readonly #pages: Page<string>[];

  constructor(pages: Page<string>[]) {
    this.#pages = pages;
  }

  *[Symbol.iterator](): Iterator<string> {
    let index: number | undefined = 0;
    while (index !== undefined) {
      const page: Page<string> = this.#pages[index]!;
      yield* page.items;
      index = page.next;
    }
  }
}

const orders = new PagedOrders([
  { items: ["order-1", "order-2"], next: 1 },
  { items: ["order-3"], next: 2 },
  { items: ["order-4", "order-5"] },
]);

for (const id of orders) console.log(id);
console.log([...orders].length, "orders total");
