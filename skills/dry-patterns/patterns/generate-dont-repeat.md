# Generate, Don't Repeat

When the same field list must appear in models, parsers, clients and docs, keep one spec and generate the copies from it.

Refs: https://openapi-generator.tech/
Example: [examples/generate-dont-repeat.py](../examples/generate-dont-repeat.py)

**Principle** — Some duplication is forced: a language, a database and a wire format each need their own text. The DRY answer is to make one spec authoritative and derive the rest with a generator. Dave Thomas (Artima interview, https://www.artima.com/articles/orthogonality-and-the-dry-principle) describes generating code and DDL from one source, and advises writing the output by hand once before automating it. The Art of Unix Programming states the same idea as its Rule of Generation. OpenAPI Generator builds clients, server stubs and docs from one document.

**Violation signals** — Each field name typed in a class, a `from_json`, a `to_json` and a TypeScript interface. Clients written by hand against a documented API.

**Fix** — Put the facts in `SPEC` and let `generate()` render the model, parser and serializer. Commit the generated file with a "generated, do not edit" header, regenerate in the build, and fail CI when the output differs. Prefer existing generators (OpenAPI, protobuf, ORM migrations) to a home-made one.

**When not to apply** — For one resource with three fields, a generator costs more than the copies. Do not hand-edit generated files: change the spec or the template. Runtime metaprogramming hides code from readers and type checkers.

**Related** — **Visitor** (`gof-patterns-typescript/patterns/visitor.md`) for generators that walk a spec tree per target; [`single-source-of-truth`](single-source-of-truth.md); [`duplicated-logic-across-layers`](duplicated-logic-across-layers.md); [`boring-technology`](../../kiss-patterns/patterns/boring-technology.md) for choosing a standard generator.
