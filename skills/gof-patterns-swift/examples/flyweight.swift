// Flyweight: share immutable intrinsic state (glyph style) across many small objects.
final class GlyphStyle: Sendable {
    let font: String
    let size: Int
    init(font: String, size: Int) {
        self.font = font
        self.size = size
    }
}

struct StyleCache {
    struct Key: Hashable { let font: String; let size: Int }
    private var styles: [Key: GlyphStyle] = [:]

    mutating func style(font: String, size: Int) -> GlyphStyle {
        let key = Key(font: font, size: size)
        if let existing = styles[key] { return existing }
        let created = GlyphStyle(font: font, size: size)
        styles[key] = created
        return created
    }

    var count: Int { styles.count }
}

// Extrinsic state (character, position) lives in the cheap struct.
struct Glyph {
    let character: Character
    let x: Int
    let style: GlyphStyle
}

var cache = StyleCache()
let text = "hello world"
var glyphs: [Glyph] = []
for (index, character) in text.enumerated() {
    let style = cache.style(font: "Menlo", size: index % 2 == 0 ? 12 : 14)
    glyphs.append(Glyph(character: character, x: index * 8, style: style))
}
print("glyphs:", glyphs.count, "shared styles:", cache.count)
print(glyphs[0].style === glyphs[2].style)
