export {};

// One way to do it: settings could be read three ways, so every reader had to learn
// all three and reviewers had to check that they agreed. The fix keeps one.

const raw: Record<string, string> = { HTTP_TIMEOUT_MS: "5000", MAX_UPLOAD_MB: "25" };

// --- Violation: three accessors over the same data ---
class Settings {
  get(key: string): string | undefined {
    return raw[key];
  }
  get timeoutMs(): number {
    return Number(raw["HTTP_TIMEOUT_MS"]);
  }
}
const settings = new Settings();
function getSetting(name: string): number {
  return parseInt(raw[name] ?? "0", 10);
}
// Three call sites, three styles:
const timeoutA = Number(settings.get("HTTP_TIMEOUT_MS"));
const timeoutB = settings.timeoutMs;
const uploadV1 = getSetting("MAX_UPLOAD_MB");

// --- Fix: one typed, parsed-once object ---
const config = {
  httpTimeoutMs: Number(raw["HTTP_TIMEOUT_MS"]),
  maxUploadMb: Number(raw["MAX_UPLOAD_MB"]),
} as const;

// --- Demo ---
console.log("timeout", config.httpTimeoutMs, timeoutA === config.httpTimeoutMs && timeoutB === config.httpTimeoutMs ? "same" : "DIFFERENT");
console.log("upload", config.maxUploadMb, uploadV1 === config.maxUploadMb ? "same" : "DIFFERENT");
