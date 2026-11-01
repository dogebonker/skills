'use strict';

const calculateTotal = (order) => {
  const items = Array.isArray(order) ? order : Object.values(order);
  return items.reduce((sum, item) => {
    if (typeof item?.price === 'number') return sum + item.price;
    if (item !== null && typeof item === 'object') {
      return sum + calculateTotal(item);
    }
    throw new TypeError(`Expected a priced item or a group, got ${item}`);
  }, 0);
};

module.exports = { calculateTotal };

if (require.main === module) {
  const json = `{
  "electronics": {
    "laptop": { "price": 1200 },
    "accessories": {
      "mouse": { "price": 25 },
      "keyboard": { "price": 75 }
    }
  },
  "books": {
    "fiction": { "price": 15 },
    "technical": { "price": 60 }
  }
}`;

  console.log(calculateTotal(JSON.parse(json)));
  try {
    calculateTotal({ books: { fiction: 'cheap' } });
  } catch (err) {
    console.log(err.name, err.message);
  }
}
