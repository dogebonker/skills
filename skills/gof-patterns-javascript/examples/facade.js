'use strict';

const createApi = (db, cache, logger) => ({
  async getUser(id) {
    const cached = cache.get(id);
    if (cached) return cached;
    const user = await db.row('User', ['*'], { id });
    cache.set(id, user);
    logger.info(`User ${id} loaded`);
    return user;
  },
});

// Checkout facade: one call over inventory, payments and shipping
const createCheckout = ({ inventory, payments, shipping }) => ({
  async placeOrder(sku, qty, amount) {
    if (!Number.isInteger(qty) || qty <= 0) {
      throw new RangeError(`Quantity must be a positive integer: ${qty}`);
    }
    if (!Number.isFinite(amount) || amount < 0) {
      throw new RangeError(`Amount must be non-negative: ${amount}`);
    }
    await inventory.reserve(sku, qty);
    let charge;
    try {
      charge = await payments.charge(amount);
    } catch (err) {
      await inventory.release(sku, qty);
      throw err;
    }
    const tracking = await shipping.ship(sku, qty);
    return { charge, tracking };
  },
});

module.exports = { createApi, createCheckout };

if (require.main === module) {
  const db = { row: async (table, fields, { id }) => ({ id, name: 'Marcus' }) };
  const api = createApi(db, new Map(), { info: console.log });

  const inventory = {
    reserve: async (sku, qty) => console.log(`reserved ${qty} ${sku}`),
    release: async (sku) => console.log(`released ${sku}`),
  };
  const payments = {
    charge: async (amount) => {
      if (amount > 100) throw new Error('card declined');
      return { id: 'ch_1', amount };
    },
  };
  const shipping = { ship: async (sku) => `track-${sku}` };
  const checkout = createCheckout({ inventory, payments, shipping });

  (async () => {
    console.log(await api.getUser(1));
    console.log(await api.getUser(1));
    console.log(await checkout.placeOrder('book', 1, 20));
    for (const [qty, amount] of [[1, 500], [0, 20]]) {
      try {
        await checkout.placeOrder('book', qty, amount);
      } catch (err) {
        console.log(`failed: ${err.message}`);
      }
    }
  })();
}
