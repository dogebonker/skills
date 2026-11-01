export {};

// Template Method: the base class fixes the order of steps; subclasses fill in the varying ones.
abstract class DataImporter {
  run(raw: string): number {
    const rows = this.parse(raw);
    const valid = rows.filter((r) => this.validate(r));
    this.save(valid);
    return valid.length;
  }

  protected abstract parse(raw: string): string[][];

  protected validate(row: string[]): boolean {
    return row.every((cell) => cell.trim() !== "");
  }

  protected save(rows: string[][]): void {
    console.log(`saved ${rows.length} rows`);
  }
}

class CsvImporter extends DataImporter {
  protected parse(raw: string): string[][] {
    return raw.split("\n").map((line) => line.split(","));
  }
}

class PipeImporter extends DataImporter {
  protected parse(raw: string): string[][] {
    return raw.split("\n").map((line) => line.split("|"));
  }

  protected override validate(row: string[]): boolean {
    return row.length === 2 && super.validate(row);
  }
}

console.log(new CsvImporter().run("a,1\nb,\nc,3"));
console.log(new PipeImporter().run("x|1\ny|2|3\nz|"));
