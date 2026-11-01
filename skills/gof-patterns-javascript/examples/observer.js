'use strict';

const { EventEmitter } = require('node:events');

class Order extends EventEmitter {
  #status = 'created';

  get status() {
    return this.#status;
  }

  setStatus(status) {
    const previous = this.#status;
    this.#status = status;
    this.emit('status', status, previous);
  }
}

module.exports = { Order };

if (require.main === module) {
  const order = new Order();
  const onStatus = (status, previous) =>
    console.log(`email: order ${previous} -> ${status}`);
  order.on('status', onStatus);
  order.once('status', (status) => console.log(`audit: first change ${status}`));
  order.setStatus('paid');
  order.off('status', onStatus);
  order.setStatus('shipped');
  console.log(order.listenerCount('status'));
}
