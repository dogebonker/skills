// Observer: subscribers are closures. Shared mutable state (the log) needs Rc<RefCell<..>>
// because several closures and main all touch it on one thread.
use std::cell::RefCell;
use std::rc::Rc;

enum Event {
    Deposit(u64),
    Withdrawal(u64),
}

#[derive(Default)]
struct Account {
    balance: i64,
    next_id: usize,
    subscribers: Vec<(usize, Box<dyn Fn(&Event)>)>,
}

impl Account {
    fn subscribe(&mut self, f: impl Fn(&Event) + 'static) -> usize {
        self.next_id += 1;
        self.subscribers.push((self.next_id, Box::new(f)));
        self.next_id
    }
    // A second unsubscribe with the same id is harmless.
    fn unsubscribe(&mut self, id: usize) {
        self.subscribers.retain(|(i, _)| *i != id);
    }
    fn publish(&self, e: &Event) {
        self.subscribers.iter().for_each(|(_, f)| f(e));
    }
    fn deposit(&mut self, n: u64) {
        self.balance += n as i64;
        self.publish(&Event::Deposit(n));
    }
    fn withdraw(&mut self, n: u64) -> Result<(), String> {
        if n as i64 > self.balance {
            return Err(format!(
                "insufficient funds: balance {}, asked {n}",
                self.balance
            ));
        }
        self.balance -= n as i64;
        self.publish(&Event::Withdrawal(n)); // only a successful withdrawal is published
        Ok(())
    }
}

fn main() {
    let log = Rc::new(RefCell::new(Vec::<String>::new()));
    let mut acct = Account::default();

    let audit = Rc::clone(&log);
    acct.subscribe(move |e| match e {
        Event::Deposit(n) => audit.borrow_mut().push(format!("+{n}")),
        Event::Withdrawal(n) => audit.borrow_mut().push(format!("-{n}")),
    });
    let alert = acct.subscribe(|e| {
        if let Event::Withdrawal(n) = e {
            if *n > 100 {
                println!("alert: large withdrawal {n}");
            }
        }
    });

    acct.deposit(500);
    acct.withdraw(150).unwrap();
    println!("{:?}", acct.withdraw(1000));
    acct.unsubscribe(alert);
    acct.unsubscribe(alert); // harmless
    acct.withdraw(120).unwrap(); // no alert any more
    println!("balance {} log {:?}", acct.balance, log.borrow());
}
