// Chain of Responsibility: an ordered list of handlers; each returns Some(reply) to stop the chain.
struct Request {
    user: Option<String>,
    calls_this_minute: u32,
    path: String,
}

trait Handler {
    fn handle(&self, req: &Request) -> Option<String>;
}

struct Auth;
struct RateLimit {
    max: u32,
}
struct Router;

impl Handler for Auth {
    fn handle(&self, req: &Request) -> Option<String> {
        req.user.is_none().then(|| "401 unauthorized".to_string())
    }
}
impl Handler for RateLimit {
    fn handle(&self, req: &Request) -> Option<String> {
        (req.calls_this_minute > self.max).then(|| "429 slow down".to_string())
    }
}
impl Handler for Router {
    fn handle(&self, req: &Request) -> Option<String> {
        Some(format!("200 served {}", req.path))
    }
}

struct Chain(Vec<Box<dyn Handler>>);

impl Chain {
    fn run(&self, req: &Request) -> String {
        self.0
            .iter()
            .find_map(|h| h.handle(req))
            .unwrap_or_else(|| "404 no handler".to_string())
    }
}

fn main() {
    let chain = Chain(vec![
        Box::new(Auth),
        Box::new(RateLimit { max: 5 }),
        Box::new(Router),
    ]);
    let req = |user: Option<&str>, calls| Request {
        user: user.map(String::from),
        calls_this_minute: calls,
        path: "/orders".into(),
    };
    println!("{}", chain.run(&req(None, 1)));
    println!("{}", chain.run(&req(Some("ana"), 9)));
    println!("{}", chain.run(&req(Some("ana"), 2)));
}
