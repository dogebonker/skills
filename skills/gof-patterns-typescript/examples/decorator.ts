export {};

// Decorator: higher-order functions wrap a function type with logging and retry, keeping its signature.
type Fetcher = (url: string) => Promise<string>;

const withLogging =
  (inner: Fetcher): Fetcher =>
  async (url) => {
    console.log(`-> ${url}`);
    const body = await inner(url);
    console.log(`<- ${body.length} chars`);
    return body;
  };

const withRetry =
  (attempts: number, baseMs = 5) =>
  (inner: Fetcher): Fetcher =>
  async (url) => {
    for (let i = 1; ; i++) {
      try {
        return await inner(url);
      } catch (err) {
        if (i >= attempts) throw err;
        console.log(`retry ${i} after: ${(err as Error).message}`);
        await new Promise((r) => setTimeout(r, baseMs * 2 ** (i - 1)));
      }
    }
  };

let calls = 0;
const flaky: Fetcher = async (url) => {
  if (++calls < 3) throw new Error("timeout");
  return `payload from ${url}`;
};

const fetcher = withLogging(withRetry(3, 5)(flaky));
fetcher("https://example.com/data").then(console.log, console.error);
