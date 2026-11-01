'use strict';

class AddressString {
  #value;

  constructor(value) {
    if (typeof value !== 'string') {
      throw new TypeError('Address must be a string');
    }
    const str = value.trim();
    if (str === '') throw new TypeError('Address must be non-empty');
    this.#value = str;
  }

  get city() {
    const index = this.#value.indexOf(',');
    if (index === -1) return this.#value;
    return this.#value.slice(0, index).trim();
  }

  toString() {
    return this.#value;
  }

  valueOf() {
    return this.#value;
  }
}

const KMH_TO_MPH = 0.621371;
const TO_KMH = { kmh: 1, mph: 1 / KMH_TO_MPH };

class SpeedValue {
  #kmh;

  constructor(value, unit = 'kmh') {
    if (typeof value !== 'number') {
      throw new TypeError('Speed must be a number');
    }
    if (value < 0) throw new TypeError('Speed must be non-negative');
    const ratio = TO_KMH[unit];
    if (ratio === undefined) throw new TypeError('Unit must be kmh or mph');
    this.#kmh = value * ratio;
  }

  get kmh() {
    return this.#kmh;
  }

  get mph() {
    return this.#kmh * KMH_TO_MPH;
  }

  toString() {
    return `${this.#kmh} km/h`;
  }

  valueOf() {
    return this.#kmh;
  }
}

module.exports = { AddressString, SpeedValue, KMH_TO_MPH };

if (require.main === module) {
  const address = new AddressString('  Roma, Via Appia 1 ');
  console.log(address.city, `${address}`);
  const speed = new SpeedValue(60, 'mph');
  console.log(speed.kmh.toFixed(1), speed.mph.toFixed(1), speed > 90);
  console.log(JSON.stringify({ address }));
  try {
    new SpeedValue(10, 'knots');
  } catch (err) {
    console.log(err.message);
  }
}
