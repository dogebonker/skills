'use strict';

const fs = require('node:fs');

const matches = (record, query) =>
  Object.entries(query).every(([key, value]) => record[key] === value);

// Memory family: records live in an array
class MemoryStorage {
  records = [];

  insert(record) {
    this.records.push(record);
  }
}

class MemoryCursor {
  constructor(query, storage) {
    this.query = query;
    this.storage = storage;
  }

  *[Symbol.iterator]() {
    for (const record of this.storage.records) {
      if (matches(record, this.query)) yield record;
    }
  }
}

// File family: one JSON record per line
class FileStorage {
  constructor(fileName) {
    this.fileName = fileName;
  }

  insert(record) {
    fs.appendFileSync(this.fileName, `${JSON.stringify(record)}\n`);
  }
}

class FileLineCursor {
  constructor(query, storage) {
    this.query = query;
    this.storage = storage;
  }

  *[Symbol.iterator]() {
    const text = fs.readFileSync(this.storage.fileName, 'utf8');
    for (const line of text.split('\n')) {
      if (!line) continue;
      const record = JSON.parse(line);
      if (matches(record, this.query)) yield record;
    }
  }
}

// Abstract factory: one key selects a consistent family of products
const dataAccess = {
  memory: {
    createDatabase: () => new MemoryStorage(),
    createCursor: (query, storage) => new MemoryCursor(query, storage),
  },
  fs: {
    createDatabase: (fileName) => new FileStorage(fileName),
    createCursor: (query, storage) => new FileLineCursor(query, storage),
  },
};

module.exports = { dataAccess };

if (require.main === module) {
  const os = require('node:os');
  const path = require('node:path');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'abstract-factory-'));
  const fileName = path.join(dir, 'storage.jsonl');
  try {
    for (const kind of ['memory', 'fs']) {
      const access = dataAccess[kind];
      const storage = access.createDatabase(fileName);
      storage.insert({ name: 'Marcus', city: 'Roma' });
      storage.insert({ name: 'Lucius', city: 'Ostia' });
      const cursor = access.createCursor({ city: 'Roma' }, storage);
      console.log(kind, [...cursor]);
    }
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}
