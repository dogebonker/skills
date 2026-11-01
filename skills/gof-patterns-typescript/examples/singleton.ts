// Singleton: an ES module is evaluated once, so an exported const is already a singleton.
// The class form below is shown for cases that need lazy creation.
class AppConfig {
  static #instance: AppConfig | undefined;
  readonly values = new Map<string, string>();

  private constructor() {
    this.values.set("env", "production");
  }

  static get instance(): AppConfig {
    return (AppConfig.#instance ??= new AppConfig());
  }
}

// Module-level alternative: no class needed.
export const settings = Object.freeze({ region: "eu-west-1", retries: 3 });

const a = AppConfig.instance;
const b = AppConfig.instance;
a.values.set("feature", "on");
console.log(a === b, b.values.get("feature"), settings.region);
