// Builder with typestate: build() only exists once the required URL is set.
use std::time::Duration;

struct HttpRequest {
    url: String,
    method: String,
    headers: Vec<(String, String)>,
    timeout: Duration,
}

struct NoUrl;
struct HasUrl(String);

struct RequestBuilder<U> {
    url: U,
    method: String,
    headers: Vec<(String, String)>,
    timeout: Duration,
}

impl RequestBuilder<NoUrl> {
    fn new() -> Self {
        RequestBuilder {
            url: NoUrl,
            method: "GET".into(),
            headers: Vec::new(),
            timeout: Duration::from_secs(30),
        }
    }
    // Consumes self and returns a builder of a different type.
    fn url(self, url: &str) -> RequestBuilder<HasUrl> {
        RequestBuilder {
            url: HasUrl(url.into()),
            method: self.method,
            headers: self.headers,
            timeout: self.timeout,
        }
    }
}

impl<U> RequestBuilder<U> {
    fn method(mut self, m: &str) -> Self {
        self.method = m.into();
        self
    }
    fn header(mut self, k: &str, v: &str) -> Self {
        self.headers.push((k.into(), v.into()));
        self
    }
    fn timeout(mut self, t: Duration) -> Self {
        self.timeout = t;
        self
    }
}

impl RequestBuilder<HasUrl> {
    fn build(self) -> HttpRequest {
        HttpRequest {
            url: self.url.0,
            method: self.method,
            headers: self.headers,
            timeout: self.timeout,
        }
    }
}

fn main() {
    let req = RequestBuilder::new()
        .method("POST")
        .header("Content-Type", "application/json")
        .url("https://api.example.com/orders")
        .timeout(Duration::from_secs(5))
        .build();
    println!(
        "{} {} {:?} {:?}",
        req.method, req.url, req.headers, req.timeout
    );
    // RequestBuilder::new().build(); // does not compile: no url yet
}
