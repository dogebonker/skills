export {};

// Abstract Factory: one object creates a matching family of products (storage + queue per cloud).
interface BlobStore {
  put(key: string, data: string): string;
}
interface JobQueue {
  enqueue(job: string): string;
}

interface CloudFactory {
  createStore(): BlobStore;
  createQueue(): JobQueue;
}

const awsFactory: CloudFactory = {
  createStore: () => ({ put: (key, data) => `s3://bucket/${key} (${data.length} bytes)` }),
  createQueue: () => ({ enqueue: (job) => `sqs queued ${job}` }),
};

const localFactory: CloudFactory = {
  createStore: () => ({ put: (key, data) => `./tmp/${key} (${data.length} bytes)` }),
  createQueue: () => ({ enqueue: (job) => `in-memory queued ${job}` }),
};

function archiveReport(cloud: CloudFactory, name: string, content: string): string[] {
  const store = cloud.createStore();
  const queue = cloud.createQueue();
  return [store.put(name, content), queue.enqueue(`index:${name}`)];
}

const factories = { aws: awsFactory, local: localFactory } satisfies Record<string, CloudFactory>;
for (const [name, factory] of Object.entries(factories)) {
  console.log(name, archiveReport(factory, "q3.csv", "id,total\n1,10"));
}
