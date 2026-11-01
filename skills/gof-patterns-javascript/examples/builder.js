'use strict';

class QueryBuilder {
  #options;

  constructor(table) {
    this.#options = { table, where: {}, limit: null, order: null };
  }

  where(cond) {
    Object.assign(this.#options.where, cond);
    return this;
  }

  order(field) {
    this.#options.order = field;
    return this;
  }

  limit(n) {
    this.#options.limit = n;
    return this;
  }

  build() {
    const where = { ...this.#options.where };
    return { ...this.#options, where };
  }
}

module.exports = { QueryBuilder };

if (require.main === module) {
  const builder = new QueryBuilder('User').where({ active: true });
  builder.order('name');
  const query = builder.limit(10).build();
  builder.where({ city: 'Roma' });
  console.log(query);
  console.log(builder.build().where);
}
