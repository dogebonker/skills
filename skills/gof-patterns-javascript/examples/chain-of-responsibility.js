'use strict';

// Each handler either answers or calls next()
const authenticate = (req, next) => {
  if (!req.user) return { status: 401, body: 'Unauthorized' };
  return next();
};

// Fixed window: counts reset when the window expires, so memory stays bounded
const rateLimit = (limit, windowMs = 1000, now = Date.now) => {
  const hits = new Map();
  let windowStart = now();
  return (req, next) => {
    if (now() - windowStart >= windowMs) {
      hits.clear();
      windowStart = now();
    }
    const count = (hits.get(req.user) ?? 0) + 1;
    hits.set(req.user, count);
    if (count > limit) return { status: 429, body: 'Too many requests' };
    return next();
  };
};

const handle = (req) => ({ status: 200, body: `Hello, ${req.user}` });

const chain = (handlers, last) => (req) => {
  const run = (i) =>
    i < handlers.length ? handlers[i](req, () => run(i + 1)) : last(req);
  return run(0);
};

module.exports = { authenticate, rateLimit, chain };

if (require.main === module) {
  let time = 0;
  const server = chain([authenticate, rateLimit(2, 1000, () => time)], handle);
  console.log(server({ user: null }));
  for (let i = 0; i < 3; i++) console.log(server({ user: 'marcus' }));
  time = 1000;
  console.log('after window:', server({ user: 'marcus' }));
}
