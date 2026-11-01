'use strict';

const flyweightPool = new Map();

const getFlyweight = ({ char, font, size }) => {
  const key = `${char}:${font}:${size}`;
  let flyweight = flyweightPool.get(key);
  if (!flyweight) {
    flyweight = Object.freeze({ char, font, size });
    flyweightPool.set(key, flyweight);
  }
  return flyweight;
};

const createChar = (char, font, size, row, col) => {
  const intrinsic = getFlyweight({ char, font, size });
  return { intrinsic, row, col };
};

module.exports = { getFlyweight, createChar };

if (require.main === module) {
  const a1 = createChar('A', 'Arial', 12, 0, 0);
  const a2 = createChar('A', 'Arial', 12, 0, 5);
  const b = createChar('B', 'Arial', 12, 0, 6);
  console.log(a1.intrinsic === a2.intrinsic, a1.intrinsic === b.intrinsic);
  const extra = getFlyweight({ char: 'C', font: 'Arial', size: 12, row: 9 });
  console.log(extra, Object.isFrozen(extra), flyweightPool.size);
}
