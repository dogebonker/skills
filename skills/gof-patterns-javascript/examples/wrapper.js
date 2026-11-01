'use strict';

const withLogging =
  (fn, label) =>
  (...args) => {
    console.log(`${label} called`, args);
    const result = fn(...args);
    console.log(`${label} returned`, result);
    return result;
  };

const wrapInterface = (anInterface, wrap) => {
  const wrapped = {};
  for (const key in anInterface) {
    const value = anInterface[key];
    const isMethod = typeof value === 'function';
    wrapped[key] = isMethod ? wrap(value, key) : value;
  }
  return wrapped;
};

class Timeout {
  constructor(fn, msec) {
    this.fn = fn;
    this.timer = setTimeout(() => {
      this.timer = null;
    }, msec);
  }

  execute(...args) {
    if (!this.timer) return null;
    clearTimeout(this.timer);
    this.timer = null;
    return this.fn(...args);
  }
}

module.exports = { withLogging, wrapInterface, Timeout };

if (require.main === module) {
  const add = withLogging((a, b) => a + b, 'add');
  add(2, 3);
  const math = wrapInterface({ pi: 3.14, square: (x) => x * x }, withLogging);
  math.square(4);
  console.log(math.pi);

  const late = new Timeout(() => 'too late', 10);
  const onTime = new Timeout((name) => `hello ${name}`, 100);
  console.log(onTime.execute('Marcus'));
  setTimeout(() => console.log('expired:', late.execute()), 20);
}
