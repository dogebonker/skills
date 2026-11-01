// Prototype: value types copy on assignment; reference types need an explicit copy method.
struct ShapeStyle {
    var color: String
    var lineWidth: Int
}

// Value type: assignment is the clone.
struct Template {
    var name: String
    var style: ShapeStyle
}

// Reference type: provide copy() because assignment would share one instance.
protocol Cloneable: AnyObject {
    func copy() -> Self
}

final class Layer: Cloneable {
    var name: String
    var opacity: Double

    init(name: String, opacity: Double) {
        self.name = name
        self.opacity = opacity
    }

    func copy() -> Self { Self(name: name, opacity: opacity) }
}

let base = Template(name: "banner", style: ShapeStyle(color: "red", lineWidth: 2))
var variant = base
variant.name = "banner-blue"
variant.style.color = "blue"
print(base.name, base.style.color, "|", variant.name, variant.style.color)

let original = Layer(name: "background", opacity: 1.0)
let clone = original.copy()
clone.opacity = 0.5
print(original.opacity, clone.opacity)
