// Flyweight: share immutable intrinsic state through Rc; keep extrinsic state per object.
use std::collections::HashMap;
use std::rc::Rc;

struct Sprite {
    name: String,
    pixels: Vec<u8>, // large, immutable, shared
}

#[derive(Default)]
struct SpriteCache {
    sprites: HashMap<String, Rc<Sprite>>,
}

impl SpriteCache {
    fn get(&mut self, name: &str) -> Rc<Sprite> {
        // Look up by &str first so a hit does not allocate a String key.
        if let Some(s) = self.sprites.get(name) {
            return Rc::clone(s);
        }
        println!("loading {name}");
        let s = Rc::new(Sprite {
            name: name.to_string(),
            pixels: vec![0; 1024],
        });
        self.sprites.insert(name.to_string(), Rc::clone(&s));
        s
    }
}

struct Tree {
    sprite: Rc<Sprite>,
    x: i32,
    y: i32,
}

fn main() {
    let mut cache = SpriteCache::default();
    let forest: Vec<Tree> = (0..5)
        .map(|i| Tree {
            sprite: cache.get("oak"),
            x: i * 10,
            y: i,
        })
        .collect();

    println!(
        "{} trees, {} sprite(s) loaded",
        forest.len(),
        cache.sprites.len()
    );
    println!("refs to oak: {}", Rc::strong_count(&forest[0].sprite));
    let t = &forest[4];
    println!(
        "{} at ({}, {}), {} bytes",
        t.sprite.name,
        t.x,
        t.y,
        t.sprite.pixels.len()
    );
}
