export {};

// Parallel hierarchies: every notification class needed a matching formatter class.
// The fix moves formatting onto the notification and deletes the second hierarchy.

// --- Violation: two hierarchies that must grow together ---
abstract class LegacyNotification {
  abstract readonly recipient: string;
}
class LegacyEmail extends LegacyNotification {
  readonly recipient: string;
  readonly subject: string;
  constructor(recipient: string, subject: string) {
    super();
    this.recipient = recipient;
    this.subject = subject;
  }
}
class LegacySms extends LegacyNotification {
  readonly recipient: string;
  constructor(recipient: string) {
    super();
    this.recipient = recipient;
  }
}

abstract class NotificationFormatter {
  abstract format(n: LegacyNotification, body: string): string;
}
class EmailFormatter extends NotificationFormatter {
  override format(n: LegacyNotification, body: string): string {
    return `To: ${n.recipient}\nSubject: ${(n as LegacyEmail).subject}\n\n${body}`;
  }
}
class SmsFormatter extends NotificationFormatter {
  override format(n: LegacyNotification, body: string): string {
    return `${n.recipient}: ${body.slice(0, 160)}`;
  }
}
function formatterFor(n: LegacyNotification): NotificationFormatter {
  if (n instanceof LegacyEmail) return new EmailFormatter();
  return new SmsFormatter();
}

// --- Fix: one hierarchy; each variant formats itself ---
interface Notification {
  format(body: string): string;
}
class EmailNotification implements Notification {
  readonly recipient: string;
  readonly subject: string;
  constructor(recipient: string, subject: string) {
    this.recipient = recipient;
    this.subject = subject;
  }
  format(body: string): string {
    return `To: ${this.recipient}\nSubject: ${this.subject}\n\n${body}`;
  }
}
class SmsNotification implements Notification {
  readonly recipient: string;
  constructor(recipient: string) {
    this.recipient = recipient;
  }
  format(body: string): string {
    return `${this.recipient}: ${body.slice(0, 160)}`;
  }
}

// --- Demo: same output from both designs ---
const body = "Your order #1042 has shipped.";
const legacy: LegacyNotification[] = [new LegacyEmail("ana@example.com", "Shipped"), new LegacySms("+351900000000")];
const current: Notification[] = [new EmailNotification("ana@example.com", "Shipped"), new SmsNotification("+351900000000")];
legacy.forEach((n, i) => {
  const before = formatterFor(n).format(n, body);
  const after = current[i]!.format(body);
  console.log(after.replace(/\n/g, " | "), before === after ? "same" : "DIFFERENT");
});
