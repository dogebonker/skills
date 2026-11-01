'use strict';

// ISP: a function receives only what it uses, not a whole app or context object. Same message.

// --- Violation: reaches through a god object, so callers and tests must rebuild all of it.
const welcomeMessageV1 = (app, id) => {
  const email = app.services.customers.findEmail(id);
  if (!email) throw new Error(`no customer ${id}`);
  return `Welcome to ${app.config.brandName}! Receipts go to ${email}.`;
};

// --- Fix: name the two things it needs. Any function and string fit (duck typing).
const welcomeMessage = (id, { findEmail, brandName }) => {
  const email = findEmail(id);
  if (!email) throw new Error(`no customer ${id}`);
  return `Welcome to ${brandName}! Receipts go to ${email}.`;
};

const createCustomerStore = () => {
  const rows = new Map();
  return {
    findEmail: (id) => rows.get(id)?.email,
    save: (c) => rows.set(c.id, c),
    remove: (id) => rows.delete(id),
    listOverdue: () => [...rows.values()].filter((c) => c.overdue),
  };
};

module.exports = { welcomeMessageV1, welcomeMessage, createCustomerStore };

if (require.main === module) {
  const customers = createCustomerStore();
  customers.save({ id: 'c-7', email: 'ana@example.com', overdue: false });
  const app = { config: { brandName: 'Lisbon Coffee', currency: 'EUR' }, services: { customers, mailer: {} } };

  console.log('violation:', welcomeMessageV1(app, 'c-7'));
  console.log('fix:      ', welcomeMessage('c-7', { findEmail: customers.findEmail, brandName: app.config.brandName }));
  console.log('same output:', welcomeMessageV1(app, 'c-7') === welcomeMessage('c-7', { findEmail: customers.findEmail, brandName: app.config.brandName }));

  // The cost shows in tests: the violation needs the nested shape, the fix needs two values.
  const fakeApp = { config: { brandName: 'Test' }, services: { customers: { findEmail: () => 't@example.com' } } };
  console.log('violation fake:', welcomeMessageV1(fakeApp, 'x'));
  console.log('fix fake:      ', welcomeMessage('x', { findEmail: () => 't@example.com', brandName: 'Test' }));
}
