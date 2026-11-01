export {};

// Prototype: clone a configured template instead of rebuilding it; structuredClone does the deep copy.
interface ReportTemplate {
  title: string;
  columns: string[];
  filters: { region: string; since: Date };
}

interface Prototype<T> {
  clone(): T;
}

class Report implements Prototype<Report> {
  data: ReportTemplate;

  constructor(data: ReportTemplate) {
    this.data = data;
  }

  clone(): Report {
    return new Report(structuredClone(this.data));
  }
}

const monthly = new Report({
  title: "Monthly sales",
  columns: ["sku", "units"],
  filters: { region: "EU", since: new Date("2026-01-01") },
});

const us = monthly.clone();
us.data.title = "Monthly sales (US)";
us.data.columns.push("revenue");
us.data.filters.region = "US";

console.log(monthly.data);
console.log(us.data);
console.log("independent copies:", monthly.data.columns !== us.data.columns);
