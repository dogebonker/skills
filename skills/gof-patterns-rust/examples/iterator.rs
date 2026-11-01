// Iterator: implement Iterator for the cursor; adaptors (filter, map, take) come for free.
struct Page {
    number: u32,
    items: Vec<u32>,
}

struct Pages<'a> {
    data: &'a [u32],
    page_size: usize,
    next_page: u32,
}

impl<'a> Pages<'a> {
    fn new(data: &'a [u32], page_size: usize) -> Result<Self, String> {
        if page_size == 0 {
            return Err("page_size must be greater than 0".into());
        }
        Ok(Pages {
            data,
            page_size,
            next_page: 1,
        })
    }
}

impl Iterator for Pages<'_> {
    type Item = Page;

    fn next(&mut self) -> Option<Page> {
        if self.data.is_empty() {
            return None;
        }
        let take = self.page_size.min(self.data.len());
        let (head, rest) = self.data.split_at(take);
        self.data = rest; // the iterator borrows the slice; nothing is copied until `to_vec`
        let page = Page {
            number: self.next_page,
            items: head.to_vec(),
        };
        self.next_page += 1;
        Some(page)
    }
}

fn main() {
    let ids = [10, 11, 12, 13, 14, 15, 16];
    for page in Pages::new(&ids, 3).unwrap() {
        println!("page {}: {:?}", page.number, page.items);
    }
    let big_pages = Pages::new(&ids, 2)
        .unwrap()
        .filter(|p| p.items.iter().sum::<u32>() > 25)
        .count();
    println!("pages summing over 25: {big_pages}");
    println!("{:?}", Pages::new(&ids, 0).err());
}
