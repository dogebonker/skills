// Builder: step-by-step construction of an immutable HTTP request value.
import Foundation

struct HTTPRequest {
    let url: URL
    let method: String
    let headers: [String: String]
    let body: Data?
}

struct HTTPRequestBuilder {
    private var url: URL
    private var method = "GET"
    private var headers: [String: String] = [:]
    private var body: Data?

    init(url: URL) { self.url = url }

    // Each step returns a modified copy, so calls chain and the builder stays a value.
    func method(_ value: String) -> Self {
        var copy = self
        copy.method = value
        return copy
    }

    func header(_ name: String, _ value: String) -> Self {
        var copy = self
        copy.headers[name] = value
        return copy
    }

    func json(_ text: String) -> Self {
        var copy = self.header("Content-Type", "application/json")
        copy.body = Data(text.utf8)
        return copy
    }

    func build() -> HTTPRequest {
        HTTPRequest(url: url, method: method, headers: headers, body: body)
    }
}

let request = HTTPRequestBuilder(url: URL(string: "https://api.example.com/orders")!)
    .method("POST")
    .header("Authorization", "Bearer token")
    .json(#"{"sku":"A-1"}"#)
    .build()
print(request.method, request.url, request.headers.keys.sorted(), request.body?.count ?? 0)
