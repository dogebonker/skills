'use strict';

// Base class fixes the algorithm skeleton, subclasses fill the steps
class Exporter {
  export(rows) {
    const columns = Object.keys(rows[0] ?? {});
    const head = this.header(columns);
    // Values in header order, so rows with another key order still line up
    const body = rows.map((r) => this.row(columns.map((c) => r[c])));
    return [head, ...body].join('\n');
  }

  header(columns) {
    return this.row(columns);
  }

  row() {
    throw new Error('row() is not implemented');
  }
}

class CsvExporter extends Exporter {
  row(values) {
    return values.join(',');
  }
}

class MarkdownExporter extends Exporter {
  row(values) {
    return `| ${values.join(' | ')} |`;
  }

  header(columns) {
    return `${super.header(columns)}\n|${columns.map(() => '---').join('|')}|`;
  }
}

module.exports = { Exporter, CsvExporter, MarkdownExporter };

if (require.main === module) {
  const rows = [{ id: 1, item: 'book' }, { item: 'pen', id: 2 }];
  console.log(new CsvExporter().export(rows));
  console.log(new MarkdownExporter().export(rows));
}
