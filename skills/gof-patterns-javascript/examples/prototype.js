'use strict';

// Literal prototype + clone
const proto = { type: 'widget', color: 'blue' };
const cloneLiteral = () => ({ ...proto });

class Point {
  #x;
  #y;

  constructor(x, y) {
    this.#x = x;
    this.#y = y;
  }

  move(x, y) {
    this.#x += x;
    this.#y += y;
  }

  clone() {
    return new Point(this.#x, this.#y);
  }

  toString() {
    return `(${this.#x}, ${this.#y})`;
  }
}

class Line {
  #start;
  #end;

  constructor(start, end) {
    this.#start = start;
    this.#end = end;
  }

  move(x, y) {
    this.#start.move(x, y);
    this.#end.move(x, y);
  }

  clone() {
    const start = this.#start.clone();
    const end = this.#end.clone();
    return new Line(start, end);
  }

  toString() {
    return `${this.#start}-${this.#end}`;
  }
}

const point = (x, y) => {
  const move = (dx, dy) => {
    x += dx;
    y += dy;
  };
  const clone = () => point(x, y);
  const position = () => ({ x, y });
  return { move, clone, position };
};

module.exports = { proto, cloneLiteral, Point, Line, point };

if (require.main === module) {
  const copy = cloneLiteral();
  copy.color = 'red';
  console.log(proto.color, copy.color);

  const line = new Line(new Point(0, 0), new Point(10, 20));
  const cloned = line.clone();
  cloned.move(2, 3);
  console.log(line.toString(), cloned.toString());

  const { move, clone, position } = point(10, 20);
  const c1 = clone();
  move(-5, 10);
  console.log(position(), c1.position());
}
