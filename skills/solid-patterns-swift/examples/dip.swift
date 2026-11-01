// DIP in Swift: the view model owns a protocol for what it needs; the
// concrete client conforms to it; the app's composition root picks it.

struct Forecast {
    let city: String
    let celsius: Double
}

// Stands in for a URLSession-backed API client.
struct LiveWeatherClient {
    func fetch(city: String) -> Forecast {
        Forecast(city: city, celsius: city == "Lisbon" ? 21.5 : 9.0)
    }
}

// --- Violation: the view model creates its own client. It cannot be shown
// in a preview or a test without the live service.
struct ForecastViewModelV1 {
    private let client = LiveWeatherClient()

    func headline(for city: String) -> String {
        let f = client.fetch(city: city)
        return "\(f.city): \(f.celsius >= 18 ? "warm" : "cold"), \(f.celsius)°C"
    }
}

// --- Fix: the abstraction is declared next to its consumer.
protocol ForecastProviding {
    func fetch(city: String) -> Forecast
}

extension LiveWeatherClient: ForecastProviding {}

struct ForecastViewModel<Provider: ForecastProviding> {
    let provider: Provider

    func headline(for city: String) -> String {
        let f = provider.fetch(city: city)
        return "\(f.city): \(f.celsius >= 18 ? "warm" : "cold"), \(f.celsius)°C"
    }
}

// A preview or test passes a canned provider; no network involved.
struct FixedForecast: ForecastProviding {
    let celsius: Double
    func fetch(city: String) -> Forecast { Forecast(city: city, celsius: celsius) }
}

let before = ["Lisbon", "Oslo"].map { ForecastViewModelV1().headline(for: $0) }
let viewModel = ForecastViewModel(provider: LiveWeatherClient())  // composition root
let after = ["Lisbon", "Oslo"].map { viewModel.headline(for: $0) }
after.forEach { print($0) }
print("same output: \(before == after)")
print("preview: \(ForecastViewModel(provider: FixedForecast(celsius: 30)).headline(for: "Porto"))")
