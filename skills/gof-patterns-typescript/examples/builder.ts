export {};

// Builder: assemble an immutable HttpRequest step by step with a fluent API.
interface HttpRequest {
  readonly method: "GET" | "POST";
  readonly url: string;
  readonly headers: Readonly<Record<string, string>>;
  readonly body?: string;
}

class RequestBuilder {
  #method: HttpRequest["method"] = "GET";
  #headers: Record<string, string> = {};
  #body?: string;

  readonly #url: string;

  constructor(url: string) {
    this.#url = url;
  }

  method(m: HttpRequest["method"]): this {
    this.#method = m;
    return this;
  }

  header(name: string, value: string): this {
    this.#headers[name] = value;
    return this;
  }

  json(payload: unknown): this {
    this.#body = JSON.stringify(payload);
    return this.method("POST").header("content-type", "application/json");
  }

  build(): HttpRequest {
    if (!this.#url.startsWith("https://")) throw new Error("https required");
    return Object.freeze({
      method: this.#method,
      url: this.#url,
      headers: { ...this.#headers },
      body: this.#body,
    });
  }
}

const req = new RequestBuilder("https://api.example.com/orders")
  .header("authorization", "Bearer token")
  .json({ sku: "A-17", qty: 2 })
  .build();
console.log(req);
