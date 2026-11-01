export {};

// Factory Method: subclasses decide which Notifier a shared workflow sends through.
interface Notifier {
  send(to: string, body: string): string;
}

class EmailNotifier implements Notifier {
  send(to: string, body: string): string {
    return `email to ${to}: ${body}`;
  }
}

class SmsNotifier implements Notifier {
  send(to: string, body: string): string {
    return `sms to ${to}: ${body.slice(0, 40)}`;
  }
}

abstract class Alert {
  protected abstract createNotifier(): Notifier;

  raise(to: string, body: string): string {
    const notifier = this.createNotifier();
    return notifier.send(to, `[ALERT] ${body}`);
  }
}

class EmailAlert extends Alert {
  protected createNotifier(): Notifier {
    return new EmailNotifier();
  }
}

class SmsAlert extends Alert {
  protected createNotifier(): Notifier {
    return new SmsNotifier();
  }
}

const alerts: Alert[] = [new EmailAlert(), new SmsAlert()];
for (const alert of alerts) {
  console.log(alert.raise("ops@example.com", "disk usage above 90%"));
}
