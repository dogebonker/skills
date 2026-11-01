// LSP in Rust: a trait impl must keep the trait's documented contract, not
// just its signature. std says `a == b` must imply `hash(a) == hash(b)`.
use std::collections::hash_map::DefaultHasher;
use std::collections::HashSet;
use std::hash::{Hash, Hasher};

// --- Violation: equality ignores case but the derived Hash does not, so
// SkuV1 cannot be used in HashSet or HashMap. Callers fall back to a slow
// workaround that only uses `==`, and must remember why.
#[derive(Debug, Clone, Hash)]
struct SkuV1(String);

impl PartialEq for SkuV1 {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq_ignore_ascii_case(&other.0)
    }
}
impl Eq for SkuV1 {}

fn unique_count_v1(skus: &[SkuV1]) -> usize {
    let mut seen: Vec<&SkuV1> = Vec::new();
    for s in skus {
        if !seen.contains(&s) {
            seen.push(s);
        }
    }
    seen.len()
}

// --- Fix: normalise once at construction, then derive all three traits so
// they agree by construction. Sku substitutes anywhere Eq + Hash is required.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Sku(String);

impl Sku {
    fn new(raw: &str) -> Self {
        Sku(raw.to_ascii_uppercase())
    }
}

fn unique_count(skus: &[Sku]) -> usize {
    skus.iter().collect::<HashSet<_>>().len()
}

fn hash_of<T: Hash>(value: &T) -> u64 {
    let mut h = DefaultHasher::new();
    value.hash(&mut h);
    h.finish()
}

fn main() {
    let raw = ["kb-101", "KB-101", "ms-220", "Ms-220", "hd-330"];
    let v1: Vec<SkuV1> = raw.iter().map(|s| SkuV1(s.to_string())).collect();
    let fixed: Vec<Sku> = raw.iter().map(|s| Sku::new(s)).collect();

    let (before, after) = (unique_count_v1(&v1), unique_count(&fixed));
    println!("violation: {before} unique, fix: {after} unique");
    println!("same output: {}", before == after);

    // The contract check that SkuV1 fails and Sku passes.
    println!(
        "SkuV1 equal values hash equal: {}",
        hash_of(&v1[0]) == hash_of(&v1[1])
    );
    println!(
        "Sku   equal values hash equal: {}",
        hash_of(&fixed[0]) == hash_of(&fixed[1])
    );
}
