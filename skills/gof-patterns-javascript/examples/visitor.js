'use strict';

// Nodes are plain data tagged by `type`, visitors are lookup objects
const expr = {
  type: 'add',
  left: { type: 'num', value: 2 },
  right: {
    type: 'mul',
    left: { type: 'num', value: 3 },
    right: { type: 'num', value: 4 },
  },
};

const visit = (visitor, node) => {
  const method = Object.hasOwn(visitor, node.type) ? visitor[node.type] : undefined;
  if (!method) throw new Error(`No visitor for ${node.type}`);
  return method(node, (child) => visit(visitor, child));
};

const evaluate = {
  num: (n) => n.value,
  add: (n, go) => go(n.left) + go(n.right),
  mul: (n, go) => go(n.left) * go(n.right),
};

const print = {
  num: (n) => String(n.value),
  add: (n, go) => `(${go(n.left)} + ${go(n.right)})`,
  mul: (n, go) => `${go(n.left)} * ${go(n.right)}`,
};

module.exports = { visit, evaluate, print };

if (require.main === module) {
  console.log(visit(print, expr), '=', visit(evaluate, expr));
}
