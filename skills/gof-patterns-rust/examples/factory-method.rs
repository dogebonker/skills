// Factory Method: a function picks the concrete Notifier; callers only see the trait.
trait Notifier {
    fn send(&self, to: &str, body: &str) -> String;
}

struct Email;
struct Sms {
    max_len: usize,
}

impl Notifier for Email {
    fn send(&self, to: &str, body: &str) -> String {
        format!("email to {to}: {body}")
    }
}

impl Notifier for Sms {
    fn send(&self, to: &str, body: &str) -> String {
        let short: String = body.chars().take(self.max_len).collect();
        format!("sms to {to}: {short}")
    }
}

enum Channel {
    Email,
    Sms,
}

// The factory method. Box<dyn> is needed because the concrete type is chosen at runtime.
fn create_notifier(channel: Channel) -> Box<dyn Notifier> {
    match channel {
        Channel::Email => Box::new(Email),
        Channel::Sms => Box::new(Sms { max_len: 10 }),
    }
}

// Client code never names Email or Sms.
fn notify_user(channel: Channel, user: &str) -> String {
    create_notifier(channel).send(user, "Your order has shipped today")
}

fn main() {
    println!("{}", notify_user(Channel::Email, "ana@example.com"));
    println!("{}", notify_user(Channel::Sms, "+351900000"));
}
