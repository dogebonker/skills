export {};

// Bridge: two independent axes (message kind, delivery channel) composed instead of subclassed.
interface Channel {
  deliver(text: string): string;
}

const slack: Channel = { deliver: (t) => `slack: ${t}` };
const pager: Channel = { deliver: (t) => `pager: ${t.toUpperCase()}` };

abstract class Message {
  protected readonly channel: Channel;
  constructor(channel: Channel) {
    this.channel = channel;
  }
  abstract send(): string;
}

class DeploySucceeded extends Message {
  private readonly version: string;
  constructor(channel: Channel, version: string) {
    super(channel);
    this.version = version;
  }
  send(): string {
    return this.channel.deliver(`deployed ${this.version}`);
  }
}

class DatabaseDown extends Message {
  send(): string {
    return this.channel.deliver("database unreachable");
  }
}

const messages: Message[] = [
  new DeploySucceeded(slack, "v1.4.2"),
  new DatabaseDown(pager),
  new DatabaseDown(slack),
];
for (const m of messages) console.log(m.send());
