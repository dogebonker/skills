# Catalog: pattern and principle findings

One entry per finding, in four families: GoF (Creational, Structural, Behavioral, Null Object), DRY, KISS and SOLID. Removing a pattern that does not pay is a KISS finding. Where two families describe one smell, one entry holds it and the others point to it. Interpreter is out of scope.

How to read an entry:
- **Heading**: family, then the finding. Principle entries carry the sibling-skill id in backticks.
- **Signals**: the code shape that makes it a candidate.
- **Confirm**: answer every question from the code, with file:line. Two or more yes answers, including the variant or copy count, make it CONFIRMED; one makes it WEAK.
- **Counter-signals**: any one that holds makes it REJECTED. A counter-signal describes code that is already simple enough. When the smell holds and only the size of the fix is in doubt, keep the finding and pick the idiom in step 4.
- **Neighbours**: how to tell it from entries of the same shape, and which entry owns a shared smell.
- **Idiom first**: the smaller form, and the target file. Paths are under `~/.claude/skills/`: `gof-patterns-<lang>/patterns/<id>.md`, `dry-patterns/patterns/<id>.md`, `kiss-patterns/patterns/<id>.md` or `solid-patterns-<lang>/patterns/<id>.md`, each with its example. `<lang>` is one of `javascript typescript go rust kotlin swift python`; `<ext>` is `js ts go rs kt swift py`. DRY and KISS examples exist in one language each, named in the entry.
- **Steps**: "<source>, confirmed" (Kerievsky, Metz, refactoring.guru) means that source states the mechanics; "derived sketch" means written for this skill. Run tests before and after each step either way.
- **Before**: the smelly shape, in TypeScript-like pseudo-code.

## GoF: Creational

### Factory Method - Introduce Polymorphic Creation with Factory Method
**Signals**: sibling classes whose main method is the same flow except for the one object each creates (`new CarAssessor()` here, `new HomeAssessor()` there). The siblings exist only for that difference.
**Confirm**: (1) Do 2 or more siblings share the flow line for line apart from the creation? (2) Has a change to the flow had to be made in every sibling (`git log -L :process:file`)? (3) Do the created objects share one interface?
**Counter-signals**: the flows differ in more than creation; there is one sibling; the created objects have unrelated interfaces.
**Neighbours**: Template Method when the varying step is behaviour, not creation. Abstract Factory when several related objects are created together. Strategy when the object could be passed in instead of created.
**Idiom first**: pass the class or a creation function as a parameter (Python class objects, JS/TS constructor or `() => X`, Kotlin `() -> X`, Swift closure or generic, Go `func() X`, Rust closure or generic with a trait bound). This often deletes the siblings. Target: `gof-patterns-<lang>/patterns/factory-method.md`, `gof-patterns-<lang>/examples/factory-method.<ext>`.
**Steps** (derived sketch): (1) extract the creation line in each sibling into a method with one name; (2) make the remaining bodies identical; (3) pull the shared method up into one base, or into one class that takes the creation function; (4) leave only the creation override per sibling, or delete the siblings; (5) delete the duplicated bodies.
**Before**:
```ts
class RefundJob  { run(c) { const v = new RefundValidator(); v.check(c); this.log(c); return v.result; } }
class ExchangeJob { run(c) { const v = new ExchangeValidator(); v.check(c); this.log(c); return v.result; } }
class RepairJob  { run(c) { const v = new RepairValidator(); v.check(c); this.log(c); return v.result; } }
```
**Sources**: https://refactoring.guru/design-patterns/factory-method ; https://refactoring.guru/replace-constructor-with-factory-method ; https://industriallogic.com/refactoring-to-patterns/catalog/polymorphicCreationFactory.html

### Factory Method - Move Creation Knowledge to Factory
**Signals**: the same `switch`/`match` that picks a concrete class to construct appears at 2 or more call sites; construction details (URLs, ids, defaults) are repeated at each site.
**Confirm**: (1) Is the same choice made at 2 or more creation sites? (2) Are there 3 or more products behind one interface? (3) Has a new product meant editing every site?
**Counter-signals**: one creation site, since that switch already is the factory and stays; products that share no interface; a value lookup with no construction.
**Neighbours**: Abstract Factory when several matching products are made per variant. Builder when one object is assembled in steps. Creation methods (named static constructors) when the problem is unclear constructors, not a choice of class.
**Idiom first**: one function `senderFor(kind)`; or parse the key into an enum once at the edge and give the enum a method that builds the product (Rust, Swift, Kotlin). Target: `gof-patterns-<lang>/patterns/factory-method.md`, `gof-patterns-<lang>/examples/factory-method.<ext>`.
**Steps** (derived sketch): (1) pin each creation site with a test; (2) extract one site's switch into a factory function; (3) replace the other sites with calls to it; (4) make concrete constructors non-public where the language allows; (5) move parsing of the key to the input boundary.
**Before**:
```ts
function sendInvoice(c)  { const s = c.channel === 'email' ? new Email(FROM) : c.channel === 'sms' ? new Sms(ID) : new Hook(URL); s.send(...); }
function sendReminder(c) { const s = c.channel === 'email' ? new Email(FROM) : c.channel === 'sms' ? new Sms(ID) : new Hook(URL); s.send(...); }
```
**Sources**: https://refactoring.guru/design-patterns/factory-method ; https://refactoring.guru/smells/switch-statements ; https://industriallogic.com/refactoring-to-patterns/catalog/creationWithFactory.html ; https://industriallogic.com/refactoring-to-patterns/catalog/classesWithFactory.html

### Abstract Factory - one variant check at many creation sites
**Signals**: a variant check (vendor, platform, region, environment) repeated at several sites, each building a different object that must match the others built for the same variant.
**Confirm**: (1) Are there 2 or more product types and 2 or more variants? (2) Would mixing variants be a bug? (3) Is the variant fixed once, at startup or per tenant?
**Counter-signals**: one product type (use Factory Method); one variant; products that combine freely.
**Neighbours**: Factory Method makes one product. Builder assembles one object in steps. Bridge splits two axes of behaviour, not creation.
**Idiom first**: one object or struct of creation functions per variant, chosen at the composition root (a JS/TS object literal, a Go struct of funcs, a Kotlin `object` per variant, a Python module per variant). Target: `gof-patterns-<lang>/patterns/abstract-factory.md`, `gof-patterns-<lang>/examples/abstract-factory.<ext>`.
**Steps** (derived sketch): (1) list products by variant in a small table; (2) give each product type one interface; (3) write one factory per variant with one create function per product; (4) choose the factory once at startup; (5) replace each creation site with a factory call.
**Before**:
```ts
const store = env === 'cloud' ? new S3Store() : new DiskStore();
// elsewhere
const queue = env === 'cloud' ? new SqsQueue() : new MemoryQueue();
```
**Sources**: https://refactoring.guru/design-patterns/abstract-factory

### Builder - replace a long or optional-heavy constructor
**Signals**: a constructor or factory with 4 or more parameters, several optional; call sites passing `null`, `None`, `false` or `""` placeholders; booleans in a row; telescoping overloads; a tree assembled by a long sequence of calls.
**Confirm**: (1) 4 or more parameters with 2 or more optional? (2) Placeholders at 2 or more call sites? (3) Do invariants span several fields, or must construction happen in steps?
**Counter-signals**: every parameter required and the list is short; the call sites already pass named arguments and leave the defaults out; one call site.
**Neighbours**: Builder - Introduce Parameter Object (next entry) when the same group travels through several functions. Creation methods when a few named configurations cover the call sites. Abstract Factory when the problem is choosing a family.
**Idiom first**: TS/JS options object with defaults; Python keyword-only `@dataclass(kw_only=True)` with defaults; Kotlin named and default arguments; Swift default arguments; Go options struct literal, or functional options when defaults need logic; Rust `Default` with struct update syntax, or builder methods taking `self`. A full Builder only when steps must be ordered or validated at the end. Target: `gof-patterns-<lang>/patterns/builder.md`, `gof-patterns-<lang>/examples/builder.<ext>`.
**Steps** (derived sketch): (1) pin construction of each existing variant with a test; (2) introduce the options shape with defaults equal to today's placeholders; (3) move call sites over one at a time; (4) remove the positional form; (5) add cross-field validation where the object is completed.
**Before**:
```ts
new Account('a1', 'Ana', 'EUR', false, null, null, true, 30);
new Account('a2', 'Rui', 'USD', true, 'PO-9', null, false, 14);
```
**Sources**: https://refactoring.guru/design-patterns/builder ; https://refactoring.guru/smells/long-parameter-list ; https://refactoring.guru/introduce-parameter-object ; https://industriallogic.com/refactoring-to-patterns/catalog/constructorCreation.html ; https://industriallogic.com/refactoring-to-patterns/catalog/compositeWithBulder.html ; https://eslint.org/docs/latest/rules/max-params

### Builder - Introduce Parameter Object: one parameter group passed through several functions
**Signals**: the same 3 or more parameters, under the same names, in the signatures of several functions that call one another; dicts or keyword bags built from that group and passed down; layers that only forward the group (Data Clumps).
**Confirm**: (1) Do 3 or more functions take the same group of 3 or more parameters (count the signatures)? (2) Is the group forwarded unchanged, or copied into dicts, at 2 or more call sites? (3) Do the values form one concept (a quote request, a trade leg) with rules that span several of them?
**Counter-signals**: the functions share only one or two parameters; each layer uses a different subset, so one object would hide what each function needs; a framework or base class fixes the signatures.
**Neighbours**: Builder (previous entry) when the problem is one constructor's long or optional-heavy list. DRY Duplicated knowledge when the copied dicts also repeat a rule. SOLID SRP when a list is long because one function does several jobs; split it first.
**Idiom first**: an immutable record of the group, built once at the outer call: Python frozen `@dataclass(kw_only=True)` with `dataclasses.replace` for variants; TS readonly `type`; Kotlin `data class` with `copy`; Swift `struct`; Go struct passed by value; Rust struct with `Default`. The target file gives the record's shape and defaults; the mechanics are refactoring-guru's. Target: `gof-patterns-<lang>/patterns/builder.md`, `gof-patterns-<lang>/examples/builder.<ext>`; mechanics in `refactoring-guru` (Introduce Parameter Object, Preserve Whole Object).
**Steps** (refactoring.guru, confirmed): (1) create an immutable record for the group; (2) add it as a parameter of the outermost function and pass a record built from the old arguments at every call; (3) delete the old parameters one by one, reading the record's fields instead, testing after each; (4) repeat one layer down, then replace the dicts built from the group with the record; (5) move logic that uses only the record's fields onto it (Move Method or Extract Method).
**Before**:
```ts
function quote(from, to, amount, network, orderType, settings) { return evaluate(from, to, amount, network, orderType, settings); }
function evaluate(from, to, amount, network, orderType, settings) { return provider.quote({ from, to, amount, network, orderType, settings }); }
```
**Sources**: https://refactoring.guru/introduce-parameter-object ; https://refactoring.guru/smells/data-clumps ; https://refactoring.guru/preserve-whole-object ; https://refactoring.guru/smells/long-parameter-list

### Prototype - copy a configured object instead of rebuilding it
**Signals**: an object copied field by field to make a variant; subclasses that differ only in initial values; the same heavy setup repeated for near-identical objects; a copy needed when only an interface type is known.
**Confirm**: (1) Field-by-field copies at 2 or more sites? (2) Must the copy work through an interface? (3) Is setup costly or long?
**Counter-signals**: a plain data copy the language already does; objects holding sockets, handles or identity that must not be duplicated.
**Neighbours**: Factory Method creates fresh objects by subclass. Memento snapshots state for restore, not for new objects.
**Idiom first**: JS/TS spread or `structuredClone`; Python `dataclasses.replace` or `copy.deepcopy`; Kotlin data class `copy()`; Swift value types; Rust `#[derive(Clone)]`; Go struct value copy. Target: `gof-patterns-<lang>/patterns/prototype.md`, `gof-patterns-<lang>/examples/prototype.<ext>`.
**Steps** (derived sketch): (1) add a copy operation on the type; (2) replace manual copies with it; (3) if presets repeat, keep a small registry of configured originals; (4) delete subclasses that only set initial values.
**Before**:
```ts
const rush = new Plan(); rush.days = base.days; rush.fee = base.fee; rush.region = base.region; rush.priority = 1;
```
**Sources**: https://refactoring.guru/design-patterns/prototype

### Singleton - Limit Instantiation with Singleton
**Signals**: a costly shared resource (connection pool, large cache) constructed repeatedly, with a measured cost.
**Confirm**: (1) Is the repeated construction measured as a cost? (2) Must exactly one instance exist for correctness? (3) Can it be created once and passed in instead?
**Counter-signals**: global access is only convenient; tests need a fresh or fake instance; passing the object works. The default is one instance created at startup and passed in; see KISS - Pattern overuse: inline a singleton.
**Neighbours**: Flyweight shares many immutable instances. A module-level instance is the light form.
**Idiom first**: create the instance once at the composition root and pass it in. If global access is truly required: ES module or Python module instance, Go package var or `sync.OnceValue`, Kotlin `object`, Swift `static let`, Rust `LazyLock`/`OnceLock`. Target: `gof-patterns-<lang>/patterns/singleton.md`, `gof-patterns-<lang>/examples/singleton.<ext>`.
**Steps** (derived sketch): (1) measure; (2) create one instance at startup; (3) pass it to each user; (4) only if passing is impossible, expose it as a module-level or lazy static value.
**Before**:
```ts
function handle(req) { const pool = new DbPool(CONFIG); return pool.query(req.sql); }
```
**Sources**: https://refactoring.guru/design-patterns/singleton ; https://industriallogic.com/refactoring-to-patterns/catalog/instantiationWithSingleton.html ; https://nodejs.org/api/modules.html

## GoF: Structural

### Adapter - Unify Interfaces with Adapter
**Signals**: 2 or more call sites convert units, field names or status codes to call one foreign API; snake_case keys inside camelCase code; strings returned by a vendor parsed at each call; one class with `if (version == N)` branches for several API versions (Extract Adapter).
**Confirm**: (1) Do 2 or more call sites, ideally 3, repeat the same conversion? (2) Is the API foreign (vendor, legacy, generated) and not yours to change? (3) Does the conversion leak vendor names or units into business code?
**Counter-signals**: you own the API, so change it; one call site, so inline the conversion; each site converts differently.
**Neighbours**: Facade simplifies a whole subsystem. Decorator keeps the interface and adds behaviour. Proxy keeps the interface and controls access.
**Idiom first**: a small module or wrapper with your names and units; Kotlin extension functions; Rust newtype with `From`/`Into`; Go small struct that satisfies an interface defined by the consumer; Swift extension or wrapper struct. Add an interface only when callers must swap providers. Target: `gof-patterns-<lang>/patterns/adapter.md`, `gof-patterns-<lang>/examples/adapter.<ext>`.
**Steps** (derived sketch): (1) pin the call sites; (2) write the adapter with the operations callers want, in domain units and errors; (3) move one call site's conversion into it; (4) move the rest; (5) make the vendor client reachable only through the adapter.
**Before**:
```ts
const r = vendor.createPayment({ amount_cents: Math.round(eur * 100), ccy: 'EUR' });
if (r.status_code !== 200) throw new Error(`failed ${r.status_code}`);
// same conversion in two more functions
```
**Sources**: https://refactoring.guru/design-patterns/adapter ; https://refactoring.guru/smells/alternative-classes-with-different-interfaces ; https://industriallogic.com/refactoring-to-patterns/catalog/interfacesWithAdapter.html ; https://industriallogic.com/refactoring-to-patterns/catalog/extractAdapter.html

### Bridge - two axes of variation multiplying classes (also DRY `parallel-hierarchies`)
**Signals**: classes named after two axes (`PdfEmailReport`, `PdfSmsReport`, `HtmlEmailReport`); parallel hierarchies where each new class in one forces one in the other; one class with branches for several backends and several front-end variants.
**Confirm**: (1) Are there two independent axes, each with 2 or more members today? (2) Does adding one member force several new classes? (3) Can the axes change separately?
**Counter-signals**: one axis only (Strategy); one backend; the combinations are few and fixed.
**Neighbours**: Strategy swaps one algorithm. Adapter retrofits one interface. Abstract Factory picks matching families. This entry also holds the DRY parallel-hierarchies smell: report one finding, family DRY when one tree should fold into the other, GoF when both axes really vary.
**Idiom first**: composition: the abstraction holds a function or small interface for the implementation axis. When only one axis really varies, move the partner's methods onto the main type and delete the second tree (the DRY fix). Target: `gof-patterns-<lang>/patterns/bridge.md`, `gof-patterns-<lang>/examples/bridge.<ext>`; DRY view: `dry-patterns/patterns/parallel-hierarchies.md`, `dry-patterns/examples/parallel-hierarchies.ts`.
**Steps** (derived sketch): (1) name both axes; (2) extract an interface for the implementation axis; (3) make the abstraction hold one; (4) replace each class-per-combination with an abstraction plus an implementation; (5) delete the combination classes.
**Before**:
```ts
class PdfEmailReport { render() { /* pdf */ } deliver() { /* email */ } }
class PdfSmsReport   { render() { /* pdf */ } deliver() { /* sms */ } }
class HtmlEmailReport { render() { /* html */ } deliver() { /* email */ } }
```
**Sources**: https://refactoring.guru/design-patterns/bridge ; https://refactoring.guru/smells/parallel-inheritance-hierarchies

### Composite - Replace One/Many Distinctions with Composite
**Signals**: code asks "single item or group?" (`Array.isArray`, `isinstance(x, list)`, a type switch on leaf versus container, `as?` casts) and recurses by hand; trees held as untyped lists (`[]any`, `[Any]`, `List<Any>`); separate code paths for one item and for many; a tree encoded in strings (Replace Implicit Tree with Composite).
**Confirm**: (1) Is the data a tree, with containers holding both leaves and containers? (2) Do 2 or more operations or call sites walk it with type checks? (3) Can leaves and containers answer the same questions?
**Counter-signals**: a flat list; leaves and containers need different operations; type checks on decoded JSON at an I/O boundary (`isinstance(x, dict)` or `isinstance(x, list)` on a vendor payload, `typeof` on a parsed body), which are defensive parsing of a foreign shape, not a tree of your own types.
**Neighbours**: Visitor when many operations run over a stable set of node types. Decorator wraps exactly one child. Iterator only traverses.
**Idiom first**: one interface or protocol with the shared operations, implemented by leaf and container (Go interface, Swift protocol, Kotlin sealed interface, Rust enum with a recursive variant or a trait, Python `Protocol`, TS union or interface). Type the children with it. Target: `gof-patterns-<lang>/patterns/composite.md`, `gof-patterns-<lang>/examples/composite.<ext>`.
**Steps** (derived sketch): (1) pin each walk with a nested example; (2) declare the component interface with the operations the walks need; (3) implement it on the leaf types; (4) make the container hold children of the component type and aggregate them; (5) replace the type checks with calls and delete the one/many duplicate paths.
**Before**:
```ts
function weight(x: unknown): number {
  if (x instanceof Item) return x.kg;
  if (x instanceof Crate) return x.tare + x.contents.map(weight).reduce((a, b) => a + b, 0);
  throw new Error('?');
}
```
**Sources**: https://refactoring.guru/design-patterns/composite ; https://industriallogic.com/refactoring-to-patterns/catalog/onemanyDistinctionsWithComposite.html ; https://industriallogic.com/refactoring-to-patterns/catalog/implicitTreeWithComposite.html

### Decorator - Move Embellishment to Decorator
**Signals**: flags (`useCache`, `logRequests`, `retries`, `addTax`) toggling optional behaviour around one core operation; subclasses for combinations of extras; a constructor that takes flags only to wrap the core.
**Confirm**: (1) Are there 2 or more independent extras around one core? (2) Does each extra have its own flag or subclass, so the combination is picked where the object is built? (3) Can each extra run before or after the core with the same signature?
**Counter-signals**: one extra that is always on, so inline it; extras tangled with the core's internals; the extra changes the interface (Adapter).
**Neighbours**: Proxy owns and controls access to one service and is not composed by the caller. Chain of Responsibility may stop the call. Strategy replaces the core instead of adding to it. Kerievsky's own warning: a 10-line class beat a 50-line Decorator for a single display tweak.
**Idiom first**: higher-order functions (`withRetry(withCache(fetch))`); Python `@decorator`; middleware chains; Go `func(next) Handler` wrappers; Kotlin class delegation `by`; Swift closure composition; Rust a wrapper struct implementing the same trait; an array of `(x) => x'` adjustments for numeric pipelines. Target: `gof-patterns-<lang>/patterns/decorator.md`, `gof-patterns-<lang>/examples/decorator.<ext>`.
**Steps** (derived sketch): (1) pin behaviour for each flag combination in use; (2) isolate the core operation behind a function or interface; (3) move one extra into a wrapper with the same signature and delete its flag; (4) repeat per extra; (5) compose the wrappers where the object was built, in the order the old code applied them.
**Before**:
```ts
async get(url) {
  if (this.cache && this.memo.has(url)) return this.memo.get(url);
  if (this.log) console.log(url);
  const body = await this.http(url);
  if (this.cache) this.memo.set(url, body);
  return body;
}
```
**Sources**: https://refactoring.guru/design-patterns/decorator ; https://industriallogic.com/refactoring-to-patterns/catalog/embellishmentToDecorator.html ; https://courses.cs.duke.edu/compsci307d/current/readings/kerievsky_preface.pdf

### Facade - one entry point for a repeated subsystem sequence
**Signals**: several clients repeat the same sequence of calls across several subsystem objects (create, configure, call, clean up).
**Confirm**: (1) Is the same orchestration repeated at 2 or more sites, ideally 3? (2) Do clients use a small slice of the subsystem? (3) Do the copies drift apart over time?
**Counter-signals**: clients need the full subsystem; the facade would mirror the subsystem method for method (Middle Man); one site.
**Neighbours**: Adapter wraps one object to fit an interface. Mediator coordinates peers that know only it. Abstract Factory when only creation is hidden.
**Idiom first**: a module-level function that runs the sequence. Target: `gof-patterns-<lang>/patterns/facade.md`, `gof-patterns-<lang>/examples/facade.<ext>`.
**Steps** (derived sketch): (1) extract the sequence from one site into a function; (2) replace the other sites; (3) leave the subsystem reachable for clients that need more; (4) split the facade if it starts collecting unrelated sequences.
**Before**:
```ts
const inv = new Inventory(db); const pay = new Payments(key); const mail = new Mailer(smtp);
inv.reserve(sku); pay.charge(card, amt); mail.receipt(email);
// same three lines in checkout, reorder and admin tools
```
**Sources**: https://refactoring.guru/design-patterns/facade ; https://refactoring.guru/smells/middle-man

### Flyweight - share immutable state across many objects
**Signals**: very many similar objects each carrying identical immutable data (glyph metrics, tile textures, price tables), with measured memory pressure.
**Confirm**: (1) Is there a memory measurement showing the problem? (2) Is the shared part immutable? (3) Are object counts in the thousands or more?
**Counter-signals**: no measurement, which rejects it outright; few objects; the shared part mutates.
**Neighbours**: Singleton is one, possibly mutable, instance. Composite leaves are often flyweights.
**Idiom first**: intern immutable values in a map keyed by their content. Target: `gof-patterns-<lang>/patterns/flyweight.md`, `gof-patterns-<lang>/examples/flyweight.<ext>`.
**Steps** (derived sketch): (1) measure; (2) split fields into shared immutable and per-use; (3) build a cache that returns one shared object per key; (4) pass per-use data as arguments; (5) measure again.
**Before**:
```ts
for (const cell of grid) cell.style = { font: 'Inter', size: 12, color: '#222', weight: 400 };
```
**Sources**: https://refactoring.guru/design-patterns/flyweight

### Proxy - move repeated access control to a stand-in
**Signals**: the same lazy creation, permission check, cache lookup or remote-call handling written around calls to one service at many call sites.
**Confirm**: (1) Do 3 or more call sites repeat the same wrapper logic? (2) Can clients stay unaware of it? (3) Does the concern belong to the service's lifecycle rather than to each caller?
**Counter-signals**: only one caller; a memoize helper already covers it; each call needs a different treatment.
**Neighbours**: Decorator is stacked by the caller to add behaviour. Adapter changes the interface. Facade simplifies a subsystem.
**Idiom first**: a wrapper with the same interface (JS `Proxy` or wrapper object, Python `functools.cache` or a wrapper class, Kotlin delegation `by`, Rust a struct implementing the same trait, Go a struct implementing the same interface, Swift a wrapper conforming to the same protocol). Target: `gof-patterns-<lang>/patterns/proxy.md`, `gof-patterns-<lang>/examples/proxy.<ext>`.
**Steps** (derived sketch): (1) extract the service interface; (2) write the proxy holding the real service; (3) move the repeated logic into the proxy; (4) construct the proxy where the service was constructed; (5) delete the call-site copies.
**Before**:
```ts
if (!user.can('read')) throw new Forbidden();
const r = cache.get(id) ?? (await api.fetch(id));
// repeated before every api.fetch
```
**Sources**: https://refactoring.guru/design-patterns/proxy

## GoF: Behavioral

### Chain of Responsibility - ordered checks that may stop the request
**Signals**: a fixed sequence of checks (authentication, validation, rate limit, cache) in one function, each able to reject or answer; the set or order differs by route, tenant or config.
**Confirm**: (1) 3 or more checks? (2) Does the set or order vary by context? (3) Should callers add checks without editing the function?
**Counter-signals**: a small set of checks always run in the same order, so plain sequential calls are clearer.
**Neighbours**: Decorator always forwards. Command turns a request into a value. Strategy picks one algorithm up front.
**Idiom first**: an array of handler functions run until one returns a result; framework middleware. Target: `gof-patterns-<lang>/patterns/chain-of-responsibility.md`, `gof-patterns-<lang>/examples/chain-of-responsibility.<ext>`.
**Steps** (derived sketch): (1) pin each rejection path; (2) extract each check into a function with one shared signature; (3) put them in a list; (4) run the list in order, stopping at the first answer; (5) let the caller build the list.
**Before**:
```ts
function handle(req) {
  if (!req.token) return deny(401);
  if (!valid(req.body)) return deny(400);
  if (overLimit(req.ip)) return deny(429);
  return serve(req);
}
```
**Sources**: https://refactoring.guru/design-patterns/chain-of-responsibility

### Command - Replace Conditional Dispatcher with Command
**Signals**: a `switch` on a request name or id where each branch runs a different action; the same name switched on again for undo, description or permissions; history kept as raw strings.
**Confirm**: (1) 3 or more actions? (2) Is there a need to queue, log, retry, undo or register actions at runtime? (3) Is the same name switched on in a second place?
**Counter-signals**: 2 actions with no undo, queue or history need; a plain callback does the job.
**Neighbours**: Strategy offers interchangeable ways to do one job; Command makes distinct operations into values. Chain of Responsibility tries handlers in order. SOLID OCP is the principle view of this smell; one finding, with `ocp` as its principle when history shows the switch edited per variant. A value that undo restores by literal (hour = 11) belongs to this finding: the command records the previous value.
**Idiom first**: a map from name to function (JS `Map`, Python dict, Go `map[string]func`, Kotlin map of lambdas or a sealed interface with `execute`/`undo`, Swift enum or closures, Rust enum with `match` or `Box<dyn FnMut>`). Objects with `execute` and `undo` only when undo is needed. Target: `gof-patterns-<lang>/patterns/command.md`, `gof-patterns-<lang>/examples/command.<ext>`.
**Steps** (Kerievsky, confirmed secondhand): (1) extract each branch body into its own function; (2) give every action the same signature, plus an undo where needed; (3) build a map from name to action; (4) replace the conditional with lookup and execute, failing loudly on unknown names; (5) record executed actions, not strings, for history.
**Before**:
```ts
switch (cmd) {
  case 'add': cart.add(arg); break;
  case 'remove': cart.remove(arg); break;
  case 'coupon': cart.apply(arg); break;
}
history.push(cmd);   // undo() switches on cmd again
```
**Sources**: https://refactoring.guru/design-patterns/command ; https://industriallogic.com/refactoring-to-patterns/catalog/conditionDispatcherWithCommand.html ; https://scrutinizer-ci.com/docs/refactorings/replace-conditional-dispatcher-with-command

### Iterator - give a custom structure its own traversal
**Signals**: clients embed the traversal of a custom structure (index juggling, a manual stack or queue); the same traversal copied into several functions; several traversal orders needed.
**Confirm**: (1) Is the traversal copied at 2 or more sites? (2) Does it expose the structure's internals to clients? (3) Are several orders needed?
**Counter-signals**: a plain array or list; the language iterator already covers it.
**Neighbours**: Composite gives the structure; Visitor gives operations over it.
**Idiom first**: a generator (JS/TS `function*` and `Symbol.iterator`, Python `yield`, Kotlin `sequence {}`, Rust `impl Iterator`, Go `iter.Seq`, Swift `Sequence`). Target: `gof-patterns-<lang>/patterns/iterator.md`, `gof-patterns-<lang>/examples/iterator.<ext>`.
**Steps** (derived sketch): (1) pin the visit order; (2) write one generator per order on the structure; (3) replace each hand-written loop with it; (4) hide the internals the loops used.
**Before**:
```ts
const stack = [root];
while (stack.length) { const n = stack.pop(); visit(n); stack.push(...n.kids); }
// same loop in export() and search()
```
**Sources**: https://refactoring.guru/design-patterns/iterator ; https://docs.python.org/3/howto/functional.html

### Mediator - route a coupled cluster through one coordinator
**Signals**: a cluster of components (form fields, panels, modules) holding references to each other and calling each other both ways; one component cannot be reused without its neighbours.
**Confirm**: (1) 3 or more components with many-to-many links? (2) Does changing one force edits in several others? (3) Is reuse blocked by the links?
**Counter-signals**: two collaborators; the mediator would only forward calls.
**Neighbours**: Observer is one-way subscription. Facade simplifies a subsystem that may still talk internally.
**Idiom first**: one coordinator function or object that receives events and calls the components; components keep no references to each other. Target: `gof-patterns-<lang>/patterns/mediator.md`, `gof-patterns-<lang>/examples/mediator.<ext>`.
**Steps** (derived sketch): (1) pick the coupled cluster; (2) create the mediator with one notify entry point; (3) make each component report to it instead of calling peers; (4) move the cross-component rules into it; (5) delete the peer references.
**Before**:
```ts
country.onChange = () => { region.reset(); zip.setPattern(country.value); submit.disable(); };
region.onChange  = () => { zip.clear(); submit.enable(); };
```
**Sources**: https://refactoring.guru/design-patterns/mediator ; https://refactoring.guru/smells/inappropriate-intimacy

### Memento - snapshot state without exposing it
**Signals**: callers save and restore an object's fields themselves to undo or roll back; private fields made public only so they can be saved; save and restore code duplicated.
**Confirm**: (1) Are snapshots needed? (2) Were fields exposed only for saving? (3) Is the save and restore code duplicated?
**Counter-signals**: the state is a small value the language copies for free; the state is large and changes often, so inverse operations (Command undo) are cheaper.
**Neighbours**: Command implements undo by inverse operations. Prototype copies to create, not to restore.
**Idiom first**: an immutable copy (Kotlin data class `copy`, Python `dataclasses.replace`, Swift struct value, Rust `Clone`, a frozen object in JS/TS). Target: `gof-patterns-<lang>/patterns/memento.md`, `gof-patterns-<lang>/examples/memento.<ext>`.
**Steps** (derived sketch): (1) pin undo behaviour; (2) add `save()` returning an opaque snapshot and `restore(snapshot)` on the object; (3) replace outside field copying with them; (4) make the exposed fields private again; (5) cap the history size.
**Before**:
```ts
const backup = { title: doc.title, body: doc.body, cursor: doc.cursor };
// ... later
doc.title = backup.title; doc.body = backup.body; doc.cursor = backup.cursor;
```
**Sources**: https://refactoring.guru/design-patterns/memento

### Observer - Replace Hard-Coded Notifications with Observer
**Signals**: after a state change, a method calls 3 or more collaborators in a row (mailer, stock, analytics); the same fan-out repeats after other state changes; the publisher's constructor takes each dependent only to notify it; a `didSet` or setter that calls several dependents.
**Confirm**: (1) 3 or more dependents, or the same fan-out at 2 or more change points? (2) Do dependents only react, with no return value used and no required order? (3) Has the list of dependents grown (`git log -L`)?
**Counter-signals**: one fixed dependent, so call it; a failure in one dependent must roll back the change, so keep explicit ordered calls; the publisher uses the dependents' results; a framework event system already exists, so use it.
**Neighbours**: Mediator when components call each other both ways. Chain of Responsibility when exactly one handler should take the event.
**Idiom first**: Node `EventEmitter` or `EventTarget`; a list of callbacks; Go slice of funcs or a channel; Kotlin `SharedFlow` or a list of lambdas; Swift closure list, Combine or Observation; Rust `Vec<Box<dyn FnMut(&Event)>>`; Python list of callables. Target: `gof-patterns-<lang>/patterns/observer.md`, `gof-patterns-<lang>/examples/observer.<ext>`.
**Steps** (derived sketch): (1) pin the side effects with fakes; (2) define an event value (name and payload); (3) add subscribe and publish to the subject; (4) register one existing dependent as a subscriber at the composition root and delete its hard-coded call; repeat; (5) remove the dependents from the subject's constructor.
**Before**:
```ts
ship(order) {
  order.status = 'shipped';
  this.mail.send(order.email, 'shipped');
  this.stock.release(order.items);
  this.metrics.count('shipped');
}
```
**Sources**: https://refactoring.guru/design-patterns/observer ; https://industriallogic.com/refactoring-to-patterns/catalog/hardCodedNotificationsWithObserver.html

### State - Replace State-Altering Conditionals with State
**Signals**: a status or state field; several methods start with a `switch`/`when`/`match` on it; branches assign the field a new value; some branches reject the call for the current state.
**Confirm**: (1) 3 or more states? (2) Do 2 or more methods branch on the same field? (3) Do the branches assign the field, so they are transitions? (4) Do states carry different data or rules?
**Counter-signals**: two states or a single boolean; one method branches; the branches only map a state to a label or number (a value lookup).
**Neighbours**: Strategy when the caller picks the variant and nothing transitions. Test: if the next variant depends on the current one and the object sets it, it is State. A type code fixed after construction points to subclasses or an enum with methods instead. SOLID OCP is the principle view of this smell; one finding, with `ocp` as its principle when history shows the switch edited per variant.
**Idiom first**: TS discriminated union with a transition function and a `never` check; Kotlin sealed class with exhaustive `when`; Rust enum with `match` returning the next state; Swift enum with associated values; Python `Enum` with a transition table keyed by (state, event); Go typed constants with a transition table. State objects only when each state carries real behaviour beyond transitions. Target: `gof-patterns-<lang>/patterns/state.md`, `gof-patterns-<lang>/examples/state.<ext>`.
**Steps** (derived sketch): (1) pin every (state, event) pair with a test, including rejected moves; (2) give the state its own closed type; (3) gather all transitions into one function or table; (4) move state-specific rules next to their state; (5) delete the old per-method conditionals.
**Before**:
```ts
pay()    { switch (this.status) { case 'draft': this.status = 'paid'; break; case 'void': throw ...; } }
refund() { switch (this.status) { case 'paid': this.status = 'refunded'; break; default: throw ...; } }
void()   { switch (this.status) { case 'draft': this.status = 'void'; break; default: throw ...; } }
```
**Sources**: https://refactoring.guru/design-patterns/state ; https://refactoring.guru/replace-type-code-with-state-strategy ; https://industriallogic.com/refactoring-to-patterns/catalog/alteringConditionalsWithState.html ; https://www.cse.iitm.ac.in/~krishna/preprints/icse17-c/icse17-c.pdf

### Strategy - Replace Conditional Logic with Strategy
**Signals**: a `switch` or if/else chain on a mode, kind or type value where each branch computes the same kind of result (a fee, a price, a score) by a different algorithm from the same inputs; the same choice made again in another function; the caller or config supplies the value.
**Confirm**: (1) Do 3 or more branches compute the same output by different logic, not just different constants? (2) Does the same value drive a branch in another function or file (count them)? (3) Is the choice made by the caller or config, not by the object's own transitions? (4) Has the branch list grown (`git log -L :fn:file`)?
**Counter-signals**: two branches with no growth; branches that return constants (a value lookup, so a map of values); the switch is the single place that builds the strategy objects; branches that differ only by a number (pass the number).
**Neighbours**: State if branches change the field they switch on. Command if each branch is a separate request to run, queue or undo. Template Method if variants share a fixed skeleton and differ in steps. Decorator if variants add to a core result instead of replacing it. SOLID OCP is the principle view of this smell; one finding, with `ocp` as its principle when history shows the switch edited per variant.
**Idiom first**: a map from key to function (JS/TS object or `Record` checked with `satisfies`, Python dict of callables, Go `map[string]func`, Kotlin `fun interface` or enum with a lambda, Swift enum with a computed property or closures, Rust enum with a method or an `Fn` closure). Use objects only when a variant needs state or several methods. When the same value drives two functions, one map from key to an object of both functions removes both switches. Target: `gof-patterns-<lang>/patterns/strategy.md`, `gof-patterns-<lang>/examples/strategy.<ext>`.
**Steps** (Kerievsky, confirmed via JetBrains walkthrough): (1) pin each branch with a test; (2) extract each branch's varying part into small functions with one signature; (3) move one branch into a strategy and delegate to it; (4) repeat for each branch; (5) replace the conditional with a lookup that picks the strategy; (6) rerun the tests.
**Before**:
```ts
function tax(order) {
  switch (order.regime) {
    case 'standard': return order.net * 0.23;
    case 'reduced':  return order.lines.filter(isFood).reduce(sumNet, 0) * 0.06;
    case 'export':   return order.destination.inEU ? order.net * 0.23 : 0;
  }
}  // invoiceNote(order) switches on order.regime too
```
**Sources**: https://refactoring.guru/design-patterns/strategy ; https://rust-unofficial.github.io/patterns/patterns/behavioural/strategy.html ; https://refactoring.guru/replace-conditional-with-polymorphism ; https://industriallogic.com/refactoring-to-patterns/catalog/conditionalWithStrategy.html ; https://www.jetbrains.com/help/idea/2023.2/replace-conditional-logic-with-strategy-pattern.html ; https://sol.sbc.org.br/index.php/sbsi/article/view/6127

### Template Method - Form Template Method
**Signals**: functions or classes that share one step sequence and differ in a few of those steps (header, row and footer formats; fetch, transform, save); copy-pasted flows.
**Confirm**: (1) Is the same step order repeated in 3 or more places (rule of three; 2 copies make it WEAK)? (2) Do the varying steps have the same inputs and outputs across copies? (3) Has the skeleton stayed stable while steps changed (history)?
**Counter-signals**: the copies differ in step order or in which steps run; 2 copies with no third in sight; variants must be chosen or combined at runtime (Strategy).
**Neighbours**: Strategy varies a whole algorithm by composition. Factory Method is the case where the varying step is object creation. DRY owns repeated facts and rules; this entry owns repeated step sequences across functions or classes, and DRY - Duplicate code inside one function owns copies within one function.
**Idiom first**: one function that takes the varying steps as parameters (functions, or a small interface or struct of functions: Go struct of funcs or interface, Kotlin lambdas, Python callables, TS object of functions). A base class with abstract steps only when a class hierarchy already exists. Target: `gof-patterns-<lang>/patterns/template-method.md`, `gof-patterns-<lang>/examples/template-method.<ext>`.
**Steps** (derived sketch): (1) pin each copy's output; (2) split each copy into the same named steps so the shared steps read identically; (3) write one skeleton that takes the varying steps; (4) move each copy's varying steps into its own step set; (5) delete the copies.
**Before**:
```ts
function toCsv(rows)  { const s = sortBy(rows, 'id'); return ['id,qty', ...s.map(r => `${r.id},${r.qty}`), `total,${s.length}`].join('\n'); }
function toMd(rows)   { const s = sortBy(rows, 'id'); return ['|id|qty|', ...s.map(r => `|${r.id}|${r.qty}|`), `${s.length} rows`].join('\n'); }
function toHtml(rows) { const s = sortBy(rows, 'id'); return ['<table>', ...s.map(r => `<tr><td>${r.id}</td></tr>`), '</table>'].join(''); }
```
**Sources**: https://refactoring.guru/design-patterns/template-method ; https://refactoring.guru/form-template-method ; https://refactoring.guru/smells/duplicate-code ; https://industriallogic.com/refactoring-to-patterns/catalog/formTemplateMethod.html ; https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)

### Visitor - Move Accumulation to Visitor
**Signals**: 2 or more functions, ideally 3, each with an `instanceof`/`isinstance`/type-switch chain over the same set of node classes; new operations keep being added while the node classes stay the same.
**Confirm**: (1) Is the same set of types checked in 3 or more operations? (2) Is the set of node types stable (history)? (3) Are operations being added?
**Counter-signals**: the node classes change often, so put a method on each class; only one or two operations; the code already uses an exhaustive match on a sum type, which is the idiomatic form; the checks test decoded JSON shapes (dict, list, string) at an I/O boundary, which is defensive parsing, not dispatch over your own node types.
**Neighbours**: Composite when leaves and containers should answer the same operations. Plain polymorphism (a method per class) when new node classes arrive more often than new operations. Strategy picks one algorithm, not one per type.
**Idiom first**: TS discriminated union with an exhaustive `switch` and a `never` check; Kotlin sealed type with exhaustive `when`; Rust enum with `match`; Swift enum with `switch`; Python `functools.singledispatch` for an open set or `match` for a closed one; Go type switch over a closed interface. Double-dispatch `accept`/`visit` only when the language lacks sum types and traversal code must be shared. Target: `gof-patterns-<lang>/patterns/visitor.md`, `gof-patterns-<lang>/examples/visitor.<ext>`.
**Steps** (derived sketch): (1) pin each operation's output on a mixed sample; (2) make the node set closed and checkable (union, sealed type, enum), or register per-type handlers; (3) rewrite one operation as an exhaustive match or dispatch; (4) repeat per operation; (5) delete the type-check chains and their fall-through throws.
**Before**:
```ts
function area(s)  { if (s instanceof Circle) return PI * s.r ** 2; if (s instanceof Rect) return s.w * s.h; throw 0; }
function label(s) { if (s instanceof Circle) return `circle ${s.r}`; if (s instanceof Rect) return `rect ${s.w}x${s.h}`; throw 0; }
function toSvg(s) { if (s instanceof Circle) return `<circle r="${s.r}"/>`; if (s instanceof Rect) return `<rect/>`; throw 0; }
```
**Sources**: https://refactoring.guru/design-patterns/visitor ; https://industriallogic.com/refactoring-to-patterns/catalog/accumulationToVisitor.html ; https://openjdk.org/jeps/441 ; https://kotlinlang.org/docs/sealed-classes.html ; https://rust-unofficial.github.io/patterns/patterns/behavioural/visitor.html

## GoF: Null Object

### Null Object - Introduce Null Object
**Signals**: the same absence check (`if (x)`, `x != null`, `x is not None`, `match Some/None`, `?:`) on the same field or return value at 3 or more sites, each substituting the same neutral behaviour (0, "none", do nothing).
**Confirm**: (1) Do 3 or more sites check the same field? (2) Do they all substitute a neutral default? (3) Can the absent case honour the same interface as the present one?
**Counter-signals**: absence is an error or needs different handling at each site; 1 or 2 sites; one-liners with `?.`, `??` or `map_or` already cover it and the defaults differ.
**Neighbours**: a do-nothing Strategy is a Null Object. An Optional type keeps absence explicit, which is right when absence matters.
**Idiom first**: a frozen default object (JS/TS `const NONE = {...}`), a `NoDiscount` implementation of the trait (Rust), a `NullAdjuster` class or a module-level default (Python), Kotlin `object NoX : X`, Swift `static let none`, Go a zero value whose methods are safe. There is no gof-patterns file for this one: the target shape is the Before rewritten so the field always holds an object.
**Steps** (derived sketch): (1) write the null implementation with neutral behaviour; (2) make the source assign or return it instead of null; (3) delete the checks one site at a time, running tests after each; (4) keep an explicit check only where absence means an error.
**Before**:
```ts
const rate   = member.plan ? member.plan.discount : 0;
const points = member.plan ? member.plan.pointsFor(total) : 0;
const badge  = member.plan ? member.plan.name : 'none';
```
**Sources**: https://refactoring.guru/introduce-null-object ; https://refactoring.guru/smells/temporary-field ; https://industriallogic.com/refactoring-to-patterns/catalog/nullObject.html

## DRY

Rules of three and coincidence decide most DRY verdicts: see SKILL.md Rules. Two related smells already have entries elsewhere:
- Parallel hierarchies (`dry-patterns/patterns/parallel-hierarchies.md`): use the Bridge entry above.
- The same step sequence copied across functions or classes: use the Template Method entry above.

### DRY - Duplicated knowledge (`single-source-of-truth`)
**Signals**: one list, rate, limit or rule written in two or more places, sometimes in different forms (`0.23`, `1.23` and `"23%"`); the same inline list in a validator and in a dropdown; comments asking to keep two places in sync.
**Confirm**: (1) If one copy changes, must every other copy change too? (2) Are there 2 or more copies today? (3) Do the copies already use different forms or disagree? Drift, copies that already disagree (a guard in one and not the other, a different default), is the strongest DRY evidence: it shows the copies were meant to match and did not stay in step, so it raises confidence. Signal 23 (one function name defined in several files) finds the copies; diff their bodies.
**Counter-signals**: the values are equal by coincidence and change for different reasons (`dry-patterns/patterns/knowledge-not-text.md`); the copies sit on both sides of a published contract owned by different teams; the value has a single reader.
**Neighbours**: DRY Magic values when a reader cannot name the literal, repeated or not. DRY Duplicated logic across layers when a whole rule is re-implemented per layer. Template Method when steps repeat, not facts. DRY Duplicate code inside one function when the copies sit in one function. KISS Dead code when one copy has no callers: delete it instead of merging it.
**Idiom first**: declare the fact once beside its main reader and derive the rest (TS `as const` array plus a derived union; Python `Enum` or module tuple; Go, Rust, Kotlin and Swift constants or enums). Target: `dry-patterns/patterns/single-source-of-truth.md`, `dry-patterns/examples/single-source-of-truth.ts`.
**Steps** (derived sketch): (1) name the fact; (2) declare it once; (3) rewrite each copy to read or derive from the declaration, running tests after each; (4) delete the leftover copies and any "keep in sync" notes.
**Before**:
```ts
if (!['PT', 'ES', 'FR'].includes(addr.country)) throw new Error('not shipped');
// elsewhere, for the form
const options = [{ value: 'PT' }, { value: 'ES' }, { value: 'FR' }];
```
**Sources**: https://en.wikipedia.org/wiki/Single_source_of_truth ; https://www.artima.com/articles/orthogonality-and-the-dry-principle ; https://refactoring.guru/smells/duplicate-code

### DRY - Duplicated logic across layers (`duplicated-logic-across-layers`)
**Signals**: the same validation or business rule written in two layers (request parsing and storage, client and server, handler and model), often with different wording for the same error.
**Confirm**: (1) Do 2 or more layers enforce the same rule? (2) Would a change to the rule need edits in each layer? (3) Do the copies already differ (bounds, messages, normalisation)?
**Counter-signals**: one check needs data only one layer has (uniqueness, stock levels); the outer check is a convenience and the inner one the real boundary, and both read one shared declaration already.
**Neighbours**: DRY Duplicated knowledge when the copy is a single value, not a rule. Chain of Responsibility when ordered checks are the issue.
**Idiom first**: one rule declaration (a function or a schema) that both layers call; the boundary layer still validates. Target: `dry-patterns/patterns/duplicated-logic-across-layers.md`, `dry-patterns/examples/duplicated-logic-across-layers.ts`.
**Steps** (derived sketch): (1) pin both layers' accept and reject cases; (2) extract the rule into one function or schema; (3) call it from the boundary layer; (4) call it from the other layer or delete that copy; (5) unify the error messages.
**Before**:
```ts
// handler
if (sku.length !== 6 || !sku.startsWith('SK')) return badRequest('invalid sku');
// repository
if (sku.length !== 6 || sku.slice(0, 2) !== 'SK') throw new Error('sku must be 6 chars starting with SK');
```
**Sources**: https://json-schema.org/overview/what-is-jsonschema ; https://refactoring.guru/smells/duplicate-code

### DRY - Duplicate code inside one function (`rule-of-three`)
**Signals**: one function with several near-identical blocks (the same call with the same keyword arguments, the same log or error block); the same lines at the start or end of every branch of a conditional; a dict or message built twice in one body.
**Confirm**: (1) Are there 3 or more copies in the function, or 2 copies of a business rule? (2) Do the copies differ only in values that can become arguments? (3) Has a fix landed in one copy and not the others?
**Counter-signals**: two copies of similar code (the rule of three waits for a third); copies that differ in step order or in which steps run; repetition that a reader needs to see side by side, such as a test's arrange blocks.
**Neighbours**: The rule of three counts copies of similar code. A copied business rule (a rate, a fee formula, a validation) gets one owner at its second copy: that is DRY Duplicated knowledge, not this entry. Template Method when the copies are whole functions or classes with the same steps. KISS Nested conditionals when the copies sit in deep branches that guards would flatten.
**Idiom first**: compute what varies first, then make one call (Extract Variable); move lines shared by every branch before or after the conditional (Consolidate Duplicate Conditional Fragments); a local helper for a longer repeated block (Extract Method). Target: `dry-patterns/patterns/rule-of-three.md`, `dry-patterns/examples/rule-of-three.py`; mechanics in `refactoring-guru` (Extract Method, Consolidate Duplicate Conditional Fragments).
**Steps** (refactoring.guru Consolidate Duplicate Conditional Fragments, confirmed; the rest derived sketch): (1) pin the function's outputs for each branch; (2) move code that opens every branch to before the conditional, and code that closes every branch to after it; (3) for copies in the middle, compute the varying values first and keep one copy of the call; (4) extract a longer repeated block into a local function.
**Before**:
```ts
if (order.fixed) { log.info('order', { id: order.id, amount, fee }); return trade({ symbol, side, amount, fee, client }); }
else             { log.info('order', { id: order.id, amount, fee }); return trade({ symbol, side, amount: amount - fee, fee, client }); }
```
**Sources**: https://refactoring.guru/consolidate-duplicate-conditional-fragments ; https://refactoring.guru/extract-method ; https://refactoring.guru/smells/duplicate-code ; https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)

### DRY - Magic values (`magic-values`)
**Signals**: unexplained numbers or strings in conditions and arithmetic (`> 1209600000`, `< 48`, `* 259200`); durations in raw seconds or milliseconds.
**Confirm**: (1) Does the literal encode a business decision a reader cannot name from the code? (2) Is it repeated, or tied to another literal that must change with it (48 hours and 172800 seconds)? (3) Would a change mean searching for the number?
**Counter-signals**: self-explaining values (`0`, `1`, dividing cents by `100`, a duration spelled as `24 * 60 * 60`); a name that only repeats the number (`THIRTY = 30`); equal literals with different meanings, which stay apart (`knowledge-not-text`).
**Neighbours**: This entry owns a literal a reader cannot name (a raw duration, an unexplained threshold), repeated or not. DRY Duplicated knowledge owns a fact a reader can name (a rate, a list, a radius) written in 2 or more places. State when a status code drives behaviour.
**Idiom first**: a named constant or enum next to its reader; durations built from units. Target: `dry-patterns/patterns/magic-values.md`, `dry-patterns/examples/magic-values.py`.
**Steps** (derived sketch): (1) name each literal by its meaning; (2) replace one use at a time; (3) derive linked values from each other (seconds from hours); (4) leave coincidental equal literals separate.
**Before**:
```ts
if (now - startedAt > 1209600000) expire(sub);
const retryAt = failedAt + attempt * 259200;
```
**Sources**: https://refactoring.guru/replace-magic-number-with-symbolic-constant

### DRY - Wrong abstraction: re-inline it (`wrong-abstraction`)
**Signals**: a shared function or class that grew flag parameters or branches, one per caller; each caller uses a different subset; new callers keep adding conditionals.
**Confirm**: (1) Do callers pass arguments that select mostly separate paths? (2) Did each new caller add a parameter or branch (history)? (3) Would the duplicated code be shorter than the conditionals?
**Counter-signals**: callers share most of the path, so extract only the differing part; the callers are stable and pass no caller-specific flags.
**Neighbours**: KISS Pattern overuse when there is one implementation and one shape. Strategy when real variation remains and a passed-in function can replace the flags.
**Idiom first**: plain code in each caller, re-extracted later only on real duplication (rule of three). Target: `dry-patterns/patterns/wrong-abstraction.md`, `dry-patterns/examples/wrong-abstraction.ts`.
**Steps** (Metz, confirmed): (1) inline the abstraction into every caller; (2) in each caller, use the arguments it passes to delete the branches it never takes; (3) delete the abstraction; (4) extract again only the duplication that remains.
**Before**:
```ts
function render(doc, isEmail, isPrint, withLogo, legacyMargins) {
  if (isEmail && !withLogo) ...; else if (isPrint && legacyMargins) ...; else ...
}
```
**Sources**: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction ; https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)

## KISS

Every GoF recommendation passes through this section: if a KISS entry below describes the proposed structure, the smaller fix wins.

### KISS - Pattern overuse: inline a singleton (`pattern-overuse`)
**Signals**: `getInstance()`, `_instance` with `__new__`, a Kotlin `object` with a mutable `var`, `static shared`, read from inside business methods so the dependency never appears in a signature; tests that reset global state.
**Confirm**: (1) Is the object read from inside functions that do not receive it? (2) Is it mutable? (3) Does anything require exactly one instance for correctness?
**Counter-signals**: a real single-resource constraint; a framework that requires it; an immutable constant (a module-level constant is fine).
**Neighbours**: SOLID DIP is the principle view (the dependency is hidden instead of passed in); report one finding. A module-level immutable value is the light form of Singleton and needs no removal.
**Idiom first**: create the object at the composition root and pass it as a constructor or function parameter. Target: `kiss-patterns/patterns/pattern-overuse.md`, `kiss-patterns/examples/pattern-overuse.ts`; mechanics in `refactoring-guru` (Add Parameter, Inline Class).
**Steps** (derived sketch; Kerievsky's table of contents names it Inline Singleton): (1) create the instance where the program starts; (2) add a parameter to the first user and pass the instance; (3) repeat for each user, running tests after each; (4) delete the global accessor and the uniqueness machinery.
**Before**:
```ts
class Rates { static instance = new Rates(); vatPct = 23; }
class Invoice { total() { return this.net * (1 + Rates.instance.vatPct / 100); } }
```
**Sources**: https://industriallogic.com/refactoring-to-patterns/catalog/inlineSingleton.html ; https://refactoring.guru/design-patterns/singleton ; https://en.wikipedia.org/wiki/Singleton_pattern

### KISS - Pattern overuse: collapse a one-implementation abstraction (`pattern-overuse`)
**Signals**: an interface, trait, protocol or ABC with exactly one implementation and no test double; a Strategy with one variant; a factory with one product, or a factory whose whole body is a constructor call; an interface that mirrors one class method for method.
**Confirm**: (1) Exactly one implementation across code and tests? (2) No outside consumers (published API, plugin point, framework contract)? (3) No second variant planned in the issue tracker?
**Counter-signals**: a published or framework surface; tests supply a fake; a seam around slow or external I/O used by tests; two or more real implementations, which make the interface justified.
**Neighbours**: SOLID OCP and DIP never justify an interface with one implementation (SKILL.md Rules). DRY Wrong abstraction when several callers each use a different part.
**Idiom first**: the concrete type or a plain function, used directly. Target: `kiss-patterns/patterns/pattern-overuse.md`, `kiss-patterns/examples/pattern-overuse.ts`; mechanics in `refactoring-guru` (Collapse Hierarchy, Inline Class).
**Steps** (derived sketch): (1) point every reference at the concrete type; (2) replace factory calls with constructor calls; (3) delete the interface or factory; (4) rename the implementation if it carried an `Impl` or `Default` suffix.
**Before**:
```ts
interface IdGenerator { next(): string }
class UuidIdGenerator implements IdGenerator { next() { return crypto.randomUUID(); } }
export const ids: IdGenerator = new UuidIdGenerator();
```
**Sources**: https://refactoring.guru/smells/lazy-class ; https://refactoring.guru/smells/speculative-generality ; https://refactoring.guru/collapse-hierarchy ; https://martinfowler.com/bliki/Yagni.html

### KISS - Needless indirection: remove a pass-through wrapper (`speculative-generality`)
**Signals**: a class whose methods forward to one field with the same name and the same arguments, adding nothing (Middle Man); a Decorator or Proxy that has lost its extra behaviour.
**Confirm**: (1) Do most methods forward unchanged? (2) Does the wrapper add no policy, translation, boundary or lifecycle control? (3) Does no caller depend on the wrapper's type?
**Counter-signals**: the wrapper is a real Proxy, Decorator, Adapter or Facade with behaviour; it cuts a dependency between modules on purpose; a ticket schedules behaviour for it.
**Neighbours**: Facade and Adapter look similar but translate or simplify. A Decorator adds behaviour around the call.
**Idiom first**: callers use the wrapped object directly. Target: `kiss-patterns/patterns/speculative-generality.md`, `kiss-patterns/examples/speculative-generality.py`; mechanics in `refactoring-guru` (Remove Middle Man).
**Steps** (derived sketch): (1) give callers the wrapped object (constructor argument or accessor); (2) switch each caller to it; (3) delete the forwarding methods; (4) delete the wrapper.
**Before**:
```ts
class UserStore {
  constructor(db) { this.db = db; }
  get(id) { return this.db.get(id); }
  put(u) { return this.db.put(u); }
}
```
**Sources**: https://refactoring.guru/smells/middle-man ; https://refactoring.guru/remove-middle-man

### KISS - Speculative generality: unused parameters, options and hooks (`speculative-generality`)
**Signals**: parameters no caller passes or the body never reads; option bags whose fields nothing reads; hook callbacks (`beforeX`, `onY`) that no caller supplies; abstract base classes with one subclass; generic parameters always bound to one type.
**Confirm**: (1) Does the body ignore the parameter or option, or does every caller leave it at the default (search all callers and tests)? (2) Is there no published API or plugin contract that outside code may use? (3) Does the compiler or linter already flag it as unused?
**Counter-signals**: a published or framework hook that outside users call; a seam a test double uses; a parameter required by an interface the function implements; a hook that callers do pass.
**Neighbours**: KISS Pattern overuse when the unused generality is a whole interface or factory. KISS Dead code when a whole function, method or class has no callers.
**Idiom first**: delete the parameter, option or hook; add it back with the first real caller. Target: `kiss-patterns/patterns/speculative-generality.md`, `kiss-patterns/examples/speculative-generality.py`.
**Steps** (derived sketch): (1) list every caller and test of the function; (2) remove the unused parameter or option from the signature and the call sites; (3) delete hook plumbing nobody supplies; (4) run the tests and the compiler's unused checks.
**Before**:
```ts
function exportReport(rows, options = {}, beforeExport?: (r) => r, format = 'csv') {
  return rows.map(toCsvLine).join('\n');
}
```
**Sources**: https://refactoring.guru/smells/speculative-generality ; https://martinfowler.com/bliki/Yagni.html

### KISS - Dead code: delete unreferenced code (`yagni`)
**Signals**: a function, method, class or top-level constant whose name appears only in its own definition (signal 24); one used only inside other dead code (signal 24, later passes); a copy its own file never uses while another file defines the same name (signal 24, `copy`); a private helper nothing calls; a byte-for-byte copy of a live function; a branch for an input no caller sends.
**Confirm**: (1) Does a search of the whole repository (app, tests, scripts, entry points and config) find no reference besides the definition? (2) Is there no dynamic reference (getattr or reflection, a string task, route or command name, a plugin registry, a decorator or framework hook)? (3) Is the symbol private, or internal to an application rather than part of a published library?
**Counter-signals**: a dynamic reference reaches it; it is the public API of a published library or SDK; a framework calls it by convention (test functions, `main`, lifecycle hooks, interface methods such as `String()` or `__str__`); a scheduled job or rare path (year-end, recovery) that logs show running.
**Neighbours**: KISS Speculative generality when the unused part is a parameter, option or hook of a live function. KISS Pattern overuse when an unused abstraction still has callers through its one implementation. DRY Duplicated knowledge when the copy is live and drifting: merge it, since only an unreferenced copy is deleted.
**Idiom first**: delete it in its own commit; version control keeps it. Target: `kiss-patterns/patterns/yagni.md` and `kiss-patterns/patterns/delete-before-adding.md`, examples `kiss-patterns/examples/yagni.ts` and `kiss-patterns/examples/delete-before-adding.py`; mechanics in `refactoring-guru` (Inline Class, Collapse Hierarchy, Remove Parameter).
**Steps** (derived sketch): (1) record the whole-repository search and the dynamic-reference check in the finding; (2) delete the definition and anything only it used; (3) run the tests and the linter or compiler; (4) commit the deletion apart from any feature work.
**Before**:
```ts
export function feeForLegacyTier(amount) { return amount * 0.015; }   // no references outside this line
function decimalsForStep(step) { return step.toString().split('.')[1]?.length ?? 0; }   // private, never called
```
**Sources**: https://refactoring.guru/smells/dead-code ; https://martinfowler.com/bliki/Yagni.html ; https://martinfowler.com/bliki/BeckDesignRules.html

### KISS - Nested conditionals (`flat-over-nested`)
**Signals**: arrow-shaped code with four or more levels of `if`/`else`/`for`; a result variable assigned deep in the nesting and returned at the end; `else` branches far from their `if`.
**Confirm**: (1) Are there 4 or more nesting levels in one function? (2) Are the outer conditions preconditions or special cases that could return early? (3) Is the normal path hidden at the deepest level?
**Counter-signals**: two equal, normal paths (a plain `if/else` shows the symmetry); nesting forced by resource scopes (`with`, `use`, `defer`) that guards cannot flatten.
**Neighbours**: State when the nesting tests a status field in several methods. Chain of Responsibility when the guards become independent, reorderable handlers. KISS Data over code when every branch only returns a value.
**Idiom first**: guard clauses that return or `continue` first, the normal path last; Swift `guard`, Kotlin `?: return`, Rust `let ... else`. Target: `kiss-patterns/patterns/flat-over-nested.md`, `kiss-patterns/examples/flat-over-nested.ts`.
**Steps** (derived sketch): (1) pin every path with a test; (2) turn the outermost special case into a guard that returns; (3) repeat inward; (4) merge guards with the same result; (5) leave the normal path unindented at the end.
**Before**:
```ts
let fee = 0;
if (order.paid) {
  if (!order.cancelled) {
    if (withinWindow(order)) { if (order.gift) fee = 2; else fee = 0; }
  }
}
return fee;
```
**Sources**: https://refactoring.guru/replace-nested-conditional-with-guard-clauses

### KISS - Premature optimization (`premature-optimization`)
**Signals**: hand-rolled caches or memo tables (often global, with no invalidation and a key that ignores some inputs), bit tricks or loop unrolling around cheap code, with no benchmark or profile in the repository.
**Confirm**: (1) Is there no measurement showing this code is hot? (2) Is the cached or tuned computation cheap (arithmetic, a small walk)? (3) Does the optimization add a correctness risk (stale entries, a key missing an input, unbounded growth)?
**Counter-signals**: a profile or benchmark exists and the change is measured; the work is I/O or network bound and the cache has invalidation; choosing a sensible algorithm or data structure up front, which is design, not optimization.
**Neighbours**: Proxy when a caching stand-in for an expensive remote service is the real need. KISS Pattern overuse when the cache is also a global singleton.
**Idiom first**: call the plain function; add a cache later with a measurement, a full key and an invalidation rule. Target: `kiss-patterns/patterns/premature-optimization.md`, `kiss-patterns/examples/premature-optimization.py`.
**Steps** (derived sketch): (1) pin outputs, including the inputs the cache key ignores; (2) replace cache reads with direct calls; (3) delete the cache; (4) if speed matters, profile first and keep the benchmark with any reintroduced cache.
**Before**:
```ts
const priceCache: Record<string, number> = {};
function price(item) { return (priceCache[item.sku] ??= item.base * 1.23); }  // ignores later changes to base
```
**Sources**: https://doi.org/10.1145/356635.356640

### KISS - Data over code: a value ladder (`data-over-code`)
**Signals**: an `if`/`switch` ladder where every branch only returns a constant, with 5 or more cases, or the same key mapped to different attributes in several functions.
**Confirm**: (1) Does every branch return a value with no other logic? (2) Are there 5 or more cases, or does the same key appear in 2 or more ladders? (3) Do new cases keep arriving?
**Counter-signals**: two to four cases in one place, which read fine as a `switch` (this is the usual verdict for a small lookup); branches with different logic or side effects; a TS `switch` with a `never` check whose exhaustiveness a plain object would lose.
**Neighbours**: Strategy when branches hold behaviour, not values. DRY Duplicated knowledge when the same key is mapped in several places.
**Idiom first**: a map or dictionary with a named default; a record per key when there are several attributes. Target: `kiss-patterns/patterns/data-over-code.md`, `kiss-patterns/examples/data-over-code.py`.
**Steps** (derived sketch): (1) pin each case; (2) move the pairs into one table; (3) replace the ladder with a lookup and a named default; (4) merge other ladders on the same key into records in the same table.
**Before**:
```ts
function zoneFee(z) { if (z === 'A') return 2; if (z === 'B') return 3; if (z === 'C') return 4; if (z === 'D') return 6; if (z === 'E') return 9; return 12; }
```
**Sources**: http://www.catb.org/esr/writings/taoup/html/ch01s06.html

## SOLID

SOLID entries point at `solid-patterns-<lang>/patterns/<id>.md` and `solid-patterns-<lang>/examples/<id>.<ext>`. Each of those files ends with the case where the principle makes code worse; read it before recommending a change.

### SOLID - SRP: one unit doing several jobs (`srp`)
**Signals**: one function or class that computes a business rule, formats output and does I/O (files, network, database); a class whose methods group into unrelated clusters touched by different people; a file that most changes touch.
**Confirm**: (1) Can you name 2 or more reasons to change that belong to different owners (finance rule, layout, storage)? (2) Do they change separately (history)? (3) Does testing the rule require the I/O?
**Counter-signals**: a large class whose methods all work on the same data for one owner (a value type such as Money or a date range is cohesive); parts that always change together; splitting would leave one-method classes that are functions in disguise.
**Neighbours**: Facade for the composing entry point after the split. Decorator when the extra job is logging or caching around a call. SOLID DIP when the I/O is a constructed dependency.
**Idiom first**: split into plain functions or modules by reason to change, and compose them in a short caller. Target: `solid-patterns-<lang>/patterns/srp.md`, `solid-patterns-<lang>/examples/srp.<ext>`.
**Steps** (derived sketch): (1) pin the output; (2) extract the pure rule into a function; (3) extract the formatting into a function; (4) leave the I/O in a thin caller that composes the two; (5) move each piece to the module its owner changes.
**Before**:
```ts
function monthEnd(path, orders) {
  const total = orders.reduce((s, o) => s + o.net, 0) * 1.23;
  const text = `Total ${total.toFixed(2)}\n` + orders.map(o => o.id).join('\n');
  fs.writeFileSync(path, text);
}
```
**Sources**: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html ; https://refactoring.guru/smells/large-class

### KISS or SRP - Long function (`srp`)
**Signals**: a function over about 80 lines (signal 25); comment banners or blank-line paragraphs that cut the body into steps; locals declared at the top and used by one block only; the same block repeated inside the body.
**Confirm**: (1) Does the function run past 80 lines (the signal 25 count)? (2) Does the body fall into 2 or more blocks that each compute one result you can name? (3) Do those blocks change for different reasons (a business rule, formatting, I/O, retries), or does history show edits landing in one block at a time? (4) Is a block repeated inside the body or in another function?
**Counter-signals**: a flat run of one-line steps, such as a table of mappings, a `match` over many cases or a configuration builder, where splitting only moves lines; generated code; blocks that share so many locals that each extracted function would take most of them (introduce a parameter object first).
**Neighbours**: report it as SOLID `srp` when the blocks change for different reasons or owners, and as KISS when one job is simply written long. DRY Duplicate code inside one function when copies make the length: extract the copy once. KISS Nested conditionals when the length is arrow-shaped nesting. Builder - Introduce Parameter Object when the extracted blocks would all take the same group of locals.
**Idiom first**: Extract Method for each block that computes one result, named after that result, until the original reads as a short sequence of calls; then group the new functions by reason to change and move each group beside the code its owner changes. Target: `solid-patterns-<lang>/patterns/srp.md`, `solid-patterns-<lang>/examples/srp.<ext>`; where duplication drives the length, `dry-patterns/patterns/rule-of-three.md`, `dry-patterns/examples/rule-of-three.py`; mechanics in `refactoring-guru` (Extract Method, Replace Temp with Query, Introduce Parameter Object).
**Steps** (refactoring.guru Extract Method, confirmed; the grouping is a derived sketch): (1) pin the function's outputs and side effects with a test; (2) extract the block with the fewest inputs into a function named after its result, passing its inputs and returning its outputs; (3) repeat block by block, running the tests after each; (4) when the original reads as a short list of calls, group the new functions by reason to change; (5) move each group to the module its owner changes.
**Before**:
```ts
function settle(order) {
  // validate the order (20 lines)
  // compute fees and the payout (30 lines)
  // call the exchange, retry on timeout (40 lines)
  // format the receipt and log it (25 lines)
}
```
**Sources**: https://refactoring.guru/extract-method ; https://refactoring.guru/smells/long-method ; https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html

### SOLID - OCP: a switch edited for every new variant (`ocp`)
**Signals**: a `switch` or if/else chain on a kind that history shows is edited each time a variant arrives, often repeated in several files.
**Confirm**: (1) Did the last variants each edit this code (`git log -L`)? (2) Is the same switch repeated elsewhere? (3) Is the set of variants open (others add them), or closed and yours?
**Counter-signals**: a closed set you own, where an exhaustive `switch` on a union, enum or sealed type lets the compiler find every site (keep it); an extension point nobody extends, which is speculative generality.
**Neighbours**: this is the principle view of the Strategy, State and Command entries above. Report one finding with family GoF and principle `ocp`, and use that entry's Confirm questions and steps; this entry adds only the history check.
**Idiom first**: as in Strategy, a table of functions keyed by variant for open sets; an exhaustive match for closed sets. Target: `solid-patterns-<lang>/patterns/ocp.md`, `solid-patterns-<lang>/examples/ocp.<ext>`.
**Steps** (derived sketch): (1) answer the history question; (2) follow the Strategy, State or Command entry's steps; (3) for a closed set, prefer the exhaustive-match idiom over a registry.
**Before**:
```ts
switch (p.method) { case 'card': return 30; case 'mbway': return 10; case 'transfer': return 0; default: throw new Error(p.method); }
// edited in every release that adds a payment method
```
**Sources**: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html

### SOLID - LSP: a subtype that breaks the parent's contract (`lsp`)
**Signals**: an override that throws "not supported", does nothing, or narrows what it accepts; callers that check `instanceof`/`is` to avoid one subtype; trait or protocol implementations that `panic`, `unimplemented!()` or `fatalError()`.
**Confirm**: (1) Does a caller written against the parent type break or need a type check for this subtype? (2) Does the subtype refuse, ignore or narrow something the parent promises? (3) Is the subtype used through the parent type somewhere?
**Counter-signals**: the parent documents the operation as optional; the subtype is never used through the parent type; the throw guards a real precondition the parent also states.
**Neighbours**: SOLID ISP when the stubs come from an interface that is too wide for some implementers; report ISP when several members are stubbed, LSP when one override breaks a promise. Template Method when subclasses must honour fixed steps.
**Idiom first**: split the capability so only types that keep the contract claim it, or replace inheritance with composition or a union. Target: `solid-patterns-<lang>/patterns/lsp.md`, `solid-patterns-<lang>/examples/lsp.<ext>`.
**Steps** (derived sketch): (1) write a test that runs the parent's contract against every subtype; (2) move the refused operation into a separate interface or capability; (3) make only the types that support it implement it; (4) delete the type checks in callers.
**Before**:
```ts
class Account { withdraw(n) { this.balance -= n; } }
class FixedDeposit extends Account { override withdraw() { throw new Error('not supported'); } }
if (!(acc instanceof FixedDeposit)) acc.withdraw(10);
```
**Sources**: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf ; https://refactoring.guru/smells/refused-bequest

### SOLID - ISP: a fat interface (`isp`)
**Signals**: an interface, trait or protocol with 5 or more members where some implementers stub members (`unimplemented!`, `fatalError`, `throw`), or where functions take it and use one member; in JavaScript, a context or service bag passed into domain code.
**Confirm**: (1) Does at least one implementer stub members? (2) Do clients use a small slice of the members? (3) Do different clients use different slices?
**Counter-signals**: a cohesive interface every caller uses whole; a single client and a single implementation, where a narrow interface "for testing" is pattern overuse (pass the concrete type or a function).
**Neighbours**: SOLID LSP for a single broken override. KISS Pattern overuse for an interface with one implementation. Adapter to fit an existing type to a narrow interface.
**Idiom first**: declare the small interface the client needs next to the client (Go and TS structural typing make existing types fit with no change); compose small traits or protocols; destructure exactly what a JS function uses. Target: `solid-patterns-<lang>/patterns/isp.md`, `solid-patterns-<lang>/examples/isp.<ext>`.
**Steps** (derived sketch): (1) list which members each client uses; (2) declare one small interface per client role; (3) change each client's parameter type to its role; (4) make implementers provide only the roles they support and delete the stubs.
**Before**:
```ts
interface Store { get(id): Doc; put(d: Doc): void; delete(id): void; search(q): Doc[]; export(): string }
class Archive implements Store { get() { throw new Error('write-only'); } delete() { throw new Error('append-only'); } /* ... */ }
function archiveAll(s: Store, docs: Doc[]) { docs.forEach(d => s.put(d)); }
```
**Sources**: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf

### SOLID - DIP: policy that builds its own infrastructure (`dip`)
**Signals**: business code that constructs or reaches for concrete infrastructure: `new HttpClient(...)`, an SMTP or database client built in a constructor, `process.env`, `datetime.now()`, `Date()`, `os.Create`, `URLSession.shared`; tests that need module patching to replace them.
**Confirm**: (1) Is the code a business rule or use case, not the composition root? (2) Does it construct or import the concrete dependency itself? (3) Would a test need the network, the clock, the file system or patching?
**Counter-signals**: the code is the composition root or `main`; the dependency is stable and pure (`Math`, your own pure helpers, value types); adding an interface with one implementation and no test double would be pattern overuse, so a parameter of the concrete type or a function is enough.
**Neighbours**: KISS Pattern overuse (singleton) when the dependency is a hidden global rather than constructed. Adapter when the vendor client's shape differs from what the policy asks for. Abstract Factory when the policy must create details.
**Idiom first**: pass the dependency in (constructor or function parameter; a function such as `now: () => Date` for clocks) and build it in the composition root. Target: `solid-patterns-<lang>/patterns/dip.md`, `solid-patterns-<lang>/examples/dip.<ext>`.
**Steps** (derived sketch): (1) pin behaviour with the real dependency or a recorded fake; (2) add a constructor or function parameter for the dependency; (3) move its construction to the composition root; (4) pass a fake in tests; (5) declare an interface owned by the policy only when a second implementation or a test double needs it.
**Before**:
```ts
class RefundService {
  private payments = new PaymentsClient(PAY_URL, process.env.KEY);
  refund(o) { if (Date.now() - o.paidAt < WINDOW) return this.payments.refund(o.id); }
}
```
**Sources**: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf
