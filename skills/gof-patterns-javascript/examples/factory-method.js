'use strict';

class Person {
  constructor(name) {
    this.name = name;
  }

  static factory(name) {
    return new Person(name);
  }
}

class Product {
  constructor(value) {
    this.field = value;
  }
}

class Creator {
  ProductType = Product;

  factoryMethod(...args) {
    return new this.ProductType(...args);
  }
}

class Circle {
  constructor(radius) {
    this.radius = radius;
  }
}

class Square {
  constructor(side) {
    this.side = side;
  }
}

// Registry instead of a switch: keys come from data (config, JSON, input)
const SHAPES = { circle: Circle, square: Square };

const createShape = (kind, size) => {
  const Shape = Object.hasOwn(SHAPES, kind) ? SHAPES[kind] : undefined;
  if (!Shape) throw new Error(`Unknown shape: ${kind}`);
  return new Shape(size);
};

module.exports = { Person, Product, Creator, SHAPES, createShape };

if (require.main === module) {
  console.log(Person.factory('Marcus'));
  console.log(new Creator().factoryMethod(1));
  console.log(createShape('circle', 2), createShape('square', 3));
  for (const kind of ['triangle', 'toString']) {
    try {
      createShape(kind, 1);
    } catch (err) {
      console.log(err.message);
    }
  }
}
