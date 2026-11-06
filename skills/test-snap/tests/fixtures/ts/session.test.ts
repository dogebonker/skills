import { it, layer } from "@effect/vitest";
import { Effect, Layer, TestClock } from "effect";
import { Session } from "./session";

it.effect("expires after ttl", () =>
  Effect.gen(function* () {
    const s = yield* Session.make({ ttl: 10 });
    yield* TestClock.adjust("11 millis");
    expect(yield* s.isExpired).toBe(true);
  }),
);

it.scoped("releases on scope close", () => Effect.void);

it.live("uses the live clock", () => Effect.void);

it.prop("roundtrips ids", [Session.Id], ([id]) => Session.Id.decode(Session.Id.encode(id)) === id);

layer(Session.layer)("with session layer", (it) => {
  it.effect("reads the user", () => Effect.void);

  it.layer(Layer.empty)("nested layer", (it) => {
    it.effect("still works", () => Effect.void);
  });
});

layer(Session.layer)((it) => {
  it.effect("unnamed layer test", () => Effect.void);
});
