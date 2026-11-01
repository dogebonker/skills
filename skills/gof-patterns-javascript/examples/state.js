'use strict';

// State table: allowed transitions as data instead of State subclasses
// Object.freeze is shallow, so each row is frozen too
const TRANSITIONS = Object.freeze({
  pending: Object.freeze({ pay: 'paid', cancel: 'cancelled' }),
  paid: Object.freeze({ ship: 'shipped', refund: 'cancelled' }),
  shipped: Object.freeze({ deliver: 'delivered' }),
  delivered: Object.freeze({}),
  cancelled: Object.freeze({}),
});

class Shipment {
  state = 'pending';

  dispatch(action) {
    const table = TRANSITIONS[this.state];
    // Own keys only: 'toString' or 'constructor' must not count as actions
    const next = Object.hasOwn(table, action) ? table[action] : undefined;
    if (!next) throw new Error(`Cannot ${action} when ${this.state}`);
    this.state = next;
    return this;
  }
}

module.exports = { TRANSITIONS, Shipment };

if (require.main === module) {
  const shipment = new Shipment();
  shipment.dispatch('pay').dispatch('ship');
  console.log(shipment.state);
  try {
    shipment.dispatch('cancel');
  } catch (err) {
    console.log(err.message);
  }
  console.log('rows frozen:', Object.isFrozen(TRANSITIONS.paid));
}
