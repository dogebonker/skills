export {};

// Flyweight: share immutable glyph styles across thousands of characters; each char stores only a reference.
interface GlyphStyle {
  readonly font: string;
  readonly size: number;
  readonly bold: boolean;
}

class StyleCache {
  private readonly styles = new Map<string, GlyphStyle>();

  get(font: string, size: number, bold: boolean): GlyphStyle {
    const key = `${font}|${size}|${bold}`;
    let style = this.styles.get(key);
    if (!style) {
      style = Object.freeze({ font, size, bold });
      this.styles.set(key, style);
    }
    return style;
  }

  get count(): number {
    return this.styles.size;
  }
}

interface Glyph {
  readonly char: string;
  readonly x: number;
  readonly style: GlyphStyle;
}

const cache = new StyleCache();
const text = "hello world".repeat(1000);
const glyphs: Glyph[] = [...text].map((char, i) => ({
  char,
  x: i * 8,
  style: char === "h" ? cache.get("Inter", 14, true) : cache.get("Inter", 14, false),
}));

console.log(`${glyphs.length} glyphs share ${cache.count} styles`);
