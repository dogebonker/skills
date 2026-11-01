'use strict';

// Strategies are plain functions in a lookup object
const shipping = {
  standard: (weight) => 5 + weight * 0.5,
  express: (weight) => 15 + weight * 1.2,
  pickup: () => 0,
};

const shippingCost = (method, weight) => {
  const strategy = Object.hasOwn(shipping, method) ? shipping[method] : undefined;
  if (!strategy) throw new Error(`Unknown shipping method: ${method}`);
  return strategy(weight);
};

module.exports = { shipping, shippingCost };

if (require.main === module) {
  for (const method of Object.keys(shipping)) {
    console.log(method, shippingCost(method, 10));
  }
}
