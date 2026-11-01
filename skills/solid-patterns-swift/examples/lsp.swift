// LSP in Swift: a subclass must keep the base class's promises. Mutable
// class hierarchies make that hard; value types plus a read-only protocol
// make it easy.

// --- Violation: an avatar crop must stay square, so SquareCropBoxV1
// silently rewrites the other side. Code written for CropBoxV1 breaks, and
// callers start checking the concrete type.
class CropBoxV1 {
    var width: Int
    var height: Int
    init(width: Int, height: Int) {
        self.width = width
        self.height = height
    }
}

final class SquareCropBoxV1: CropBoxV1 {
    init(side: Int) { super.init(width: side, height: side) }
    override var width: Int {
        didSet { if height != width { height = width } }
    }
    override var height: Int {
        didSet { if width != height { width = height } }
    }
}

func bannerAreaV1(_ box: CropBoxV1) -> Int {
    if box is SquareCropBoxV1 { return box.width * box.height }  // the LSP smell
    box.height = box.width / 3
    return box.width * box.height
}

// --- Fix: the shared protocol promises only what every crop can keep.
// Values are immutable; changing size means making a new value.
protocol Crop {
    var width: Int { get }
    var height: Int { get }
}

extension Crop {
    var area: Int { width * height }
}

struct FreeCrop: Crop {
    let width: Int
    let height: Int
}

struct AvatarCrop: Crop {
    let side: Int
    var width: Int { side }
    var height: Int { side }
}

// Only a free crop can take banner proportions, and the type says so.
func banner(from crop: FreeCrop) -> FreeCrop {
    FreeCrop(width: crop.width, height: crop.width / 3)
}

func area(of crop: any Crop) -> Int { crop.area }

let before = [bannerAreaV1(CropBoxV1(width: 800, height: 600)), bannerAreaV1(SquareCropBoxV1(side: 256))]
let after = [banner(from: FreeCrop(width: 800, height: 600)).area, area(of: AvatarCrop(side: 256))]
print("violation: \(before) fix: \(after)")
print("same output: \(before == after)")
