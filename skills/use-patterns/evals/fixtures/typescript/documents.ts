export class Heading { constructor(readonly title: string, readonly level: number) {} }
export class Paragraph { constructor(readonly text: string) {} }
export class Table { constructor(readonly rows: string[][]) {} }
export class Figure { constructor(readonly caption: string, readonly src: string) {} }
export type Block = Heading | Paragraph | Table | Figure;
const words = (s: string): number => s.split(/\s+/).filter(Boolean).length;

export function wordCount(blocks: Block[]): number {
  let total = 0;
  for (const block of blocks) {
    if (block instanceof Heading) total += words(block.title);
    else if (block instanceof Paragraph) total += words(block.text);
    else if (block instanceof Table) total += block.rows.flat().length;
    else if (block instanceof Figure) total += words(block.caption);
  }
  return total;
}

export function toHtml(blocks: Block[]): string {
  return blocks.map((block) => {
    if (block instanceof Heading) return `<h${block.level}>${block.title}</h${block.level}>`;
    if (block instanceof Paragraph) return `<p>${block.text}</p>`;
    if (block instanceof Table) return `<table>${block.rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</table>`;
    if (block instanceof Figure) return `<figure><img src="${block.src}"><figcaption>${block.caption}</figcaption></figure>`;
    throw new Error('unknown block');
  }).join('\n');
}

export function toPlainText(blocks: Block[]): string {
  return blocks.map((block) => {
    if (block instanceof Heading) return block.title.toUpperCase();
    if (block instanceof Paragraph) return block.text;
    if (block instanceof Table) return block.rows.map((r) => r.join(' | ')).join('\n');
    if (block instanceof Figure) return `[${block.caption}]`;
    throw new Error('unknown block');
  }).join('\n\n');
}

export function exporterFor(format: 'html' | 'text'): (blocks: Block[]) => string {
  switch (format) {
    case 'html': return toHtml;
    case 'text': return toPlainText;
  }
}

export class ReportFetcher {
  private readonly cache = new Map<string, string>();
  constructor(
    private readonly fetchText: (url: string) => Promise<string>,
    private readonly useCache: boolean, private readonly retries: number, private readonly logRequests: boolean,
  ) {}

  async fetch(url: string): Promise<string> {
    const cached = this.cache.get(url);
    if (this.useCache && cached !== undefined) return cached;
    if (this.logRequests) console.log(`GET ${url}`);
    let lastError: unknown;
    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const body = await this.fetchText(url);
        if (this.useCache) this.cache.set(url, body);
        return body;
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError;
  }
}

export class Exporter {
  export(blocks: Block[]): string { return toPlainText(blocks); }
  append(existing: string, blocks: Block[]): string { return `${existing}\n\n${this.export(blocks)}`; }
}

export class PdfExporter extends Exporter {
  override export(blocks: Block[]): string { return `%PDF-1.7 ${toPlainText(blocks).length} chars`; }
  override append(): string { throw new Error('append is not supported for PDF'); }
}

export function addChapter(exporter: Exporter, existing: string, chapter: Block[]): string {
  if (exporter instanceof PdfExporter) return exporter.export(chapter);
  return exporter.append(existing, chapter);
}

export interface RenderOptions {
  locale?: string;
  theme?: 'light' | 'dark';
  plugins?: Array<(html: string) => string>;
}

export function renderReport(blocks: Block[], options: RenderOptions = {}, beforeRender?: (blocks: Block[]) => Block[]): string {
  return `<article>${toHtml(blocks)}</article>`;
}

const DAY_MS = 24 * 60 * 60 * 1000;

export class DateRange {
  constructor(readonly start: Date, readonly end: Date) {
    if (end < start) throw new Error('end before start');
  }
  days(): number { return Math.round((this.end.getTime() - this.start.getTime()) / DAY_MS); }
  contains(d: Date): boolean { return d >= this.start && d <= this.end; }
  overlaps(o: DateRange): boolean { return this.start <= o.end && o.start <= this.end; }
  intersect(o: DateRange): DateRange | null { return this.overlaps(o) ? new DateRange(new Date(Math.max(+this.start, +o.start)), new Date(Math.min(+this.end, +o.end))) : null; }
  shift(days: number): DateRange { return new DateRange(new Date(+this.start + days * DAY_MS), new Date(+this.end + days * DAY_MS)); }
  equals(o: DateRange): boolean { return +this.start === +o.start && +this.end === +o.end; }
  toString(): string { return `${this.start.toISOString().slice(0, 10)}..${this.end.toISOString().slice(0, 10)}`; }
}
