# Signals: searches per language

Each language section has a table and a `sh` block. The table says what each search looks for, what a hit means, and which `catalog.md` entry it feeds. The block holds the commands under the same IDs. Every command ends in `.`, the scope directory it runs from. A hit is a candidate to read in full, never a finding by itself.

Signals 1 to 14 mostly feed GoF entries and KISS pattern overuse; 15 to 25 feed DRY, KISS and SOLID entries. The number after the language prefix means the same thing in every language.

## Running a block

SKILL.md step 2 runs a whole block in one call from the scope directory. The block reads three variables:
- `SKILL_DIR` (required): this skill's directory. Signals 5, 24 and 25 pipe through the awk helpers in `$SKILL_DIR/scripts/`.
- `RG_EXCLUDE` (optional): one ripgrep glob for source files of the language to leave out, such as `'**/providers/**'`, or `'**/{providers,migrations}/**'` for several. The block's first line wraps `rg` in a function that adds `-g "!$RG_EXCLUDE"`, so every command honors it, the counted `--no-filename` pipelines included. When you run one command by hand, append `-g '!**/providers/**'` to it instead. It is redundant for build and cache output: `-t <lang>` already limits every command to the language's source files, and rg skips binary, hidden and gitignored files, so `__pycache__/*.pyc`, `node_modules` or `target/` never need it.
- `REPO_ROOT` (optional, default `.`): where signal 24 counts references. Set it to the repository root so tests, scripts, config and entry points count as callers. `RG_EXCLUDE` does not apply to this count, so excluded code still counts as a caller. This count reads every file type, so the command leaves out the language's build and cache directories by glob (`__pycache__`, `node_modules`, `dist`, `build`, `target`, `.build`, `.gradle`, `vendor`) and relies on rg's binary-file skip for the rest; adding `-a` or `--binary` would undo that.

## Reading the output

Signal 5 prints one line per signature, `path:line: name (N params)`, adding `keyword-only` when a bare `*` makes the later arguments named.

Some signals have no regex that can see the problem, so their commands group things for you to compare by eye:
- S7 groups classes and functions by shared name parts, one labelled line per group: `N subclasses of Base`, `N classes named *Suffix`, `N functions named prefix*`. A family of three or more with the same step order is the hit.
- S2 and S11 (type checks): a check on decoded JSON at an I/O boundary, such as `isinstance(x, dict)` or `isinstance(x, list)` on a vendor payload, `typeof` on a parsed body or `as?` on a JSON dictionary, is defensive parsing, not a Composite or Visitor. Triage ranks those hits last, in `[boundary]` clusters, when the enclosing definition line or the file path says parse, normalize, extract, from_json or payload.
- S15 counts repeated literals. Two equal literals are one hit to read, not a finding: ask whether they change for the same reason. The string count leaves out dict and map keys (`"k": v`, a value on the same line), subscript keys (`x["k"]`), Go struct tags and, in Python, `.get("k")`, because those are mostly log fields (`extra={...}`) and vendor field names; `case "k":` labels still count, and so does a key that is a business fact wherever it appears as a value.
- S17 counts definitions per file and finds I/O calls. A file near the top of the count that also does I/O is the hit.
- S21 finds hook-shaped names and defaulted option bags. Compilers see unused parameters better: `tsc --noEmit --noUnusedParameters`, kotlinc's "parameter is never used" warning, rustc's `unused_variables` warning.
- S23 lists each name defined in more than one file, with the files, private names first. A shared name is the strongest drift signal: diff the bodies, since copies that already disagree are the strongest DRY evidence. A name that an interface, trait, protocol or abstract base in the scan declares is tagged `(override)` and sorted last; clear it unless the bodies should be one. Kotlin and Swift `override` functions never reach this list.
- S24 lists dead-code candidates for the KISS - Dead code entry, whose counter-signals (dynamic references, published API) decide each one. It counts words outside comment lines in every file type under `REPO_ROOT`; a use is any word outside the name's own definition lines. Definitions include top-level constants and tables. Three kinds of line:
  - no tag: no use anywhere;
  - `(pass N: used only by f, g)`: every use sits inside definitions found dead by earlier passes. When you clear `f` as live (a published API, a dynamic reference), clear what only `f` uses with it;
  - `(copy: ...)`: a top-level definition its own file never uses, while other files define the same name, and no file that uses the name without defining it sits in the same directory or names its file or directory. Read the import lines of the listed files before deleting it.
  A name that is also a common word elsewhere (`status`, `method`) never reaches this list; data read only by dead code under such a name shows up in the wider read of step 2.
- S25 prints `path:line: name (N lines)` for every function over 80 lines, longest first. A function runs to the next line indented no deeper than its definition, so the count includes its trailing blank lines.

## Triage

Step 2 ranks the saved scan output instead of reading it line by line. Run this from the same scope directory, with the language's `-t` type, `RG_EXCLUDE` as in the scan, and `DEF` set to the definition pattern in the language's 23 command (Python: `DEF='^\s*(?:async\s+)?def\s+(\w+)'`):

```sh
{ rg -n -H -P -t py ${RG_EXCLUDE:+--glob=!$RG_EXCLUDE} "$DEF" . | sed 's/^/D:/'; rg -c -H -t py ${RG_EXCLUDE:+--glob=!$RG_EXCLUDE} '^' . | sed 's/^/N:/'; cat <scan file>; } | awk -f "$SKILL_DIR/scripts/triage.awk"
```

The output has two parts:
- One row per cluster, the hits that share an enclosing definition, ranked by hit count and then by the definition's length. Columns: rank, hits, cumulative hits, lines, `path:line` of the definition, the signal ids that hit it, and the definition line. The enclosing definition is the nearest one above the hit; hits above a file's first definition form a `<module>` cluster. Signal 2 and 11 hits in parsing code (see Reading the output) form separate clusters marked `[boundary]`, ranked after every other cluster. The header line gives the total hit count and the `[boundary]` share, so the not-triaged count is that total minus the cumulative hits of the last cluster read.
- `# lists`: the counted outputs that carry no file:line (signals 7, 9, 13, 15, 17, 23 and the like), grouped by signal id.

## Numeric thresholds (optional)

Use these when the project already runs the tool, or as a rough bar when reading a hit. They are lint defaults, not pattern verdicts.

| Measure | Default | Source |
|---|---|---|
| Parameters per function | more than 3 | ESLint `max-params` https://eslint.org/docs/latest/rules/max-params |
| Parameters per function | 10 or more | PMD `ExcessiveParameterList` https://docs.pmd-code.org/latest/pmd_rules_java_design.html |
| Cyclomatic complexity | 20 per function | ESLint `complexity` https://eslint.org/docs/latest/rules/complexity |
| Cyclomatic complexity | 10 per method, 80 per class | PMD `CyclomaticComplexity` (same PMD page) |
| Cognitive complexity | 15 | PMD `CognitiveComplexity` (same PMD page) |
| Statements per switch label | 10 | PMD `SwitchDensity` (same PMD page) |
| Methods per class | 10, getters and setters excluded | PMD `TooManyMethods` (same PMD page) |
| Fields per class | 15 | PMD `TooManyFields` (same PMD page) |
| Exhaustive switch on a union or enum | every member, or a `default` | typescript-eslint `switch-exhaustiveness-check` https://typescript-eslint.io/rules/switch-exhaustiveness-check/ |

## JavaScript

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| JS1 | `switch`, and comparisons of a kind/type/mode/status field to string literals | a branch on a discriminator; count its cases and find every other branch on the same field | Strategy, State, Command, Factory Method |
| JS2 | `instanceof` or `typeof` checks | type dispatch; a chain of them over one value is the hit | Visitor, Composite, Strategy |
| JS3 | `else if` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| JS4 | boolean literal passed as an argument | a flag that picks behaviour inside the callee | Strategy, Decorator, Builder |
| JS5 | functions with 4+ parameters; calls passing `null`/`undefined` placeholders | a long or optional-heavy parameter list | Builder, Builder - Introduce Parameter Object |
| JS6 | loops over listener lists; state assignment followed by calls; 3+ consecutive collaborator calls | hand-rolled or hard-coded notification | Observer, Mediator |
| JS7 | subclass counts per base; function name prefix families | sibling bodies to compare for the same step order | Template Method, Strategy, Factory Method |
| JS8 | top-level `let`/`var`, `getInstance`, exported `new` instances | shared or global mutable object | Singleton, KISS - Pattern overuse (singleton) |
| JS9 | base classes with one subclass; abstract-method throws | an abstraction with one implementation | KISS - Pattern overuse (one implementation) |
| JS10 | methods that return `this.x.sameName(sameArgs)` | a pass-through wrapper when most methods of a class match | KISS - Needless indirection, Decorator, Proxy |
| JS11 | `Array.isArray`, recursion over `children`/`items` | one/many distinction or a tree walked by hand | Composite, Visitor, Iterator |
| JS12 | calls on a name ending in client, api, sdk, gateway or vendor; snake_case keys; x100 or /100 unit conversions; third-party imports and declared types (then search calls on instances of those types) | a foreign API shape converted at call sites | Adapter, Facade |
| JS13 | null and truthiness checks, grouped by property | the same absence check repeated | Null Object |
| JS14 | a factory whose whole body is `return new X(...)` | a factory with nothing to decide | KISS - Pattern overuse (one implementation) |
| JS15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| JS16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| JS17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| JS18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| JS19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| JS20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| JS21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| JS22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| JS23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| JS24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| JS25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# JS1
rg -n -t js 'switch\s*\(' .
rg -n -t js -i "\.\w*(kind|type|mode|status|state|role|tier|method|action|format|category)\w*\s*[!=]==?\s*['\"]" .
# JS2
rg -n -t js '\binstanceof\b|typeof\s+[\w.]+\s*[!=]==' .
# JS3
rg -n -t js '\belse\s+if\s*\(' .
# JS4
rg -n -t js '\w\s*\([^()]*\b(true|false)\s*[,)]' .
# JS5
rg -U -o -n -H -t js -P '(?:function\s*(\w*)|(constructor)|^[ \t]*(?:(?:static|async)\s+)*(?!(?:if|for|while|switch|catch|return|function)\b)(\w+))\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)\s*\{' -r '@@${1}${2}${3}@@${4}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t js '\(([^()]*,)?\s*(null|undefined)\s*,' .
# JS6
rg -n -t js -i '(listeners|subscribers|observers|handlers|callbacks|hooks)\w*\s*\.\s*(forEach|map)\(|for\s*\(.*\bof\s+[\w.]*(listeners|subscribers|observers|handlers|callbacks|hooks)' .
rg -n -t js -A6 '\.(status|state)\s*=[^=]' .
rg -n -t js -U '(\n\s*this\.\w+\.\w+\([^\n]*){3,}' .
# JS7
rg -o -N --no-filename -t js 'class\s+\w+\s+extends\s+(\w+)' -r '$1' . | sort | uniq -c | sort -rn | awk '{print $1, "subclasses of " $2}'
rg -o -N --no-filename -t js 'function\s+([a-z]+)[A-Z]\w*' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2 {print $1, "functions named " $2 "*"}'
# JS8
rg -n -t js '^(let|var)\s+\w+|getInstance\s*\(|static\s+#?_?instance\b|^(module\.)?exports(\.\w+)?\s*=\s*new\s|^export\s+(default\s+)?(const\s+\w+\s*=\s*)?new\s' .
# JS9
rg -n -t js -i "throw new Error\(['\"\`](not implemented|abstract|subclass)" .
# JS10
rg -n -t js -U -P '(\w+)\s*\(([^)]*)\)\s*\{\s*return\s+this\.#?\w+\.\1\(\2\);?\s*\}' .
# JS11
rg -n -t js 'Array\.isArray\(|\.(children|parts|items|nodes|contents)\b.*\.(map|forEach|reduce|flatMap)\(' .
# JS12
rg -n -t js '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(' .
rg -n -t js '\b[a-z]+_[a-z_]+\s*:|\*\s*100\b|/\s*100\b' .
rg -n -t js "^\s*import\s.+from\s+['\"][^./]|require\(['\"][^./]" .
# JS13
rg -o -N --no-filename -t js '(?:if\s*\(\s*!?|return\s+)(\w+\.\w+)\s*(?:\)|\?\s|[!=]==?\s*(?:null|undefined))' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -n -t js '[!=]==?\s*(null|undefined)\b|\?\.|\?\?' .
# JS14
rg -n -t js -U -P '(?:static\s+)?(?:create|make|build|new)\w*\s*\([^)]*\)\s*\{\s*return\s+new\s+\w+\([^)]*\);?\s*\}' .
# JS15
rg -o -N --no-filename -t js '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t js -P '(?<=\bcase )\x27[^\x27\n]{2,}\x27|(?<=[\w)\]])\[\s*\x27[^\x27\n]*\x27(*SKIP)(*F)|\x27[^\x27\n]*\x27(?=:[ \t]*[^\s/])(*SKIP)(*F)|\x27[^\x27\n]?\x27(*SKIP)(*F)|\x27[^\x27\n]{2,}\x27' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -n -t js "\[\s*'[^']+'(\s*,\s*'[^']+'){2,}\s*\]|/\^[^/\n]+/" .
rg -o -N --no-filename -t js '(?:[!=]==?|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# JS16
rg -n -t js '^( {8,}|\t{4,})(\} )?(if|else|for|while|switch|try)\b' .
# JS17
rg -n -t js -P '\b(fs\.\w+|(?<![.\w])fetch\((?![^)]*\)\s*[:{])|readFile|writeFile|\.query\(|process\.env|localStorage)' .
rg -c -t js '^\s*(async\s+)?(function\s+\w+|class\s+\w+|(static\s+)?#?\w+\s*\([^)]*\)\s*\{)' . | sort -t: -k2 -rn
# JS18
rg -n -t js -i "throw new \w*Error\(['\"\`][^'\"\`]*(not supported|unsupported|not implemented|read-only|cannot be)" .
rg -n -t js '^\s+(?!if|for|while|switch|catch|constructor)\w+\s*\([^)]*\)\s*\{\s*\}' -P .
# JS19
rg -n -t js '\b(app|ctx|context|deps|services|container|options|opts)\.\w+\.\w+' .
# JS20
rg -n -t js -P 'new\s+\w*(Client|Pool|Connection|Database|Db|Gateway|Mailer|Smtp|Redis|Http|Api|Logger)\w*\(|new Date\(\)|Date\.now\(\)|performance\.now\(\)|\bset(Timeout|Interval)\(|(?<![.\w])fetch\((?![^)]*\)\s*[:{])|process\.env\b' .
rg -n -t js '=\s*(new\s+)?[\w.]+\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# JS21
rg -n -t js '\b(on|before|after|pre|post|will|did)[A-Z]\w*\s*[=:?(,)]|\w+\s*=\s*\{\}\s*[,)]' .
# JS22
rg -n -t js -i '\b\w*(cache|memo)\w*\s*=\s*(new Map|\{\}|\[\])' .
# JS23
{ rg -U -o -N --no-filename -t js -P "(\w+)\s*\([^)]*\)\s*\{\s*throw\s+new\s+\w*Error\(\s*['\"\`](?i:not implemented|abstract|subclass)" -r 'B:$1' .; rg -o -N -H -t js -P '^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*=>|\w+\s*=>)|^\s*(?:(?:static|async|get|set)\s+)*#?(?!(?:if|for|while|switch|catch|return|function)\b)(\w+)\s*\([^)]*\)\s*\{' -r '$1$2$3' . | sort -u; } | awk -F: '$1 == "B" {b[$2]; next} $NF !~ /^(constructor|main)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print ((n in b) ? 2 : (n ~ /^_/) ? 0 : 1), c[n], n ":" f[n] ((n in b) ? " (override)" : "")}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# JS24
{ d='^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*=>|\w+\s*=>)|^\s*(?:(?:static|async|get|set)\s+)*#?(?!(?:if|for|while|switch|catch|return|function)\b)(\w+)\s*\([^)]*\)\s*\{|^(?:export\s+)?(?:const|let|var)\s+(\w+)'; w='^\s*(?://|/\*|\*(?:\s|/|$)).*(*SKIP)(*F)|\w+'; g='!**/{node_modules,dist,build}/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t js -P "$d" -r 'D $1$2$3$4' .; rg -n -H -t js '' . | sed 's/^/L /'; rg -n -H -o -t js -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t js -g "$g" -P "$d" -r 'X $1$2$3$4' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(constructor|main)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# JS25
{ rg -n -H -o -t js -P '^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*=>|\w+\s*=>)|^\s*(?:(?:static|async|get|set)\s+)*#?(?!(?:if|for|while|switch|catch|return|function)\b)(\w+)\s*\([^)]*\)\s*\{' -r 'D $1$2$3' .; rg -n -H -t js '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

JS9: also read the JS7 `subclasses of` lines; a base class with a count of 1 is the hit.

## TypeScript

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| TS1 | `switch`, and comparisons of a kind/type/mode/status field to string literals | a branch on a discriminator; count its cases and find every other branch on the same field | Strategy, State, Command, Factory Method |
| TS2 | `instanceof`, `typeof`, `.kind ===` checks | type dispatch; a chain of them over one value is the hit | Visitor, Composite, Strategy |
| TS3 | `else if` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| TS4 | `boolean` parameters and fields; boolean literal arguments | a flag that picks behaviour | Strategy, Decorator, Builder |
| TS5 | signatures with 4+ parameters (multi-line too); `null`/`undefined` placeholders | a long or optional-heavy parameter list | Builder, Builder - Introduce Parameter Object |
| TS6 | loops over listener lists; state assignment followed by calls; 3+ consecutive collaborator calls | hand-rolled or hard-coded notification | Observer, Mediator |
| TS7 | subclass counts per base; function name prefix families | sibling bodies to compare for the same step order | Template Method, Strategy, Factory Method |
| TS8 | top-level `let`, `getInstance`, exported `new` instances | shared or global mutable object | Singleton, KISS - Pattern overuse (singleton) |
| TS9 | interfaces and their `implements` count | an interface with exactly one implementation | KISS - Pattern overuse (one implementation) |
| TS10 | methods that return `this.x.sameName(sameArgs)` | a pass-through wrapper when most methods of a class match | KISS - Needless indirection, Decorator, Proxy |
| TS11 | `Array.isArray`, recursion over `children`/`items` | one/many distinction or a tree walked by hand | Composite, Visitor, Iterator |
| TS12 | calls on a name ending in client, api, sdk, gateway or vendor; snake_case keys; x100 or /100 unit conversions; third-party imports and declared types (then search calls on instances of those types) | a foreign API shape converted at call sites | Adapter, Facade |
| TS13 | null and truthiness checks, grouped by property | the same absence check repeated | Null Object |
| TS14 | a factory whose whole body is `return new X(...)` | a factory with nothing to decide | KISS - Pattern overuse (one implementation) |
| TS15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| TS16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| TS17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| TS18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| TS19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| TS20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| TS21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| TS22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| TS23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| TS24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| TS25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# TS1
rg -n -t ts 'switch\s*\(' .
rg -n -t ts -i "\.\w*(kind|type|mode|status|state|role|tier|method|action|format|category)\w*\s*[!=]==?\s*['\"]" .
# TS2
rg -n -t ts '\binstanceof\b|typeof\s+[\w.]+\s*[!=]==|\.kind\s*[!=]==' .
# TS3
rg -n -t ts '\belse\s+if\s*\(' .
# TS4
rg -n -t ts '\w+\??\s*:\s*boolean\s*[,)=;]' .
rg -n -t ts '\w\s*\([^()]*\b(true|false)\s*[,)]' .
# TS5
rg -U -o -n -H -t ts -P '(?:function\s+(\w+)|(constructor)|^[ \t]*(?:(?:public|private|protected|static|async)\s+)*(?!(?:if|for|while|switch|catch|return|function)\b)(\w+))\s*(?:<[^>]*>)?\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)\s*(?::[^{};]*)?\{' -r '@@${1}${2}${3}@@${4}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t ts '\(([^()]*,)?\s*(null|undefined)\s*,' .
# TS6
rg -n -t ts -i '(listeners|subscribers|observers|handlers|callbacks|hooks)\w*\s*\.\s*(forEach|map)\(|for\s*\(.*\bof\s+[\w.]*(listeners|subscribers|observers|handlers|callbacks|hooks)' .
rg -n -t ts -A6 '\.(status|state)\s*=[^=]' .
rg -n -t ts -U '(\n\s*this\.\w+\.\w+\([^\n]*){3,}' .
# TS7
rg -o -N --no-filename -t ts 'class\s+\w+\s+extends\s+(\w+)' -r '$1' . | sort | uniq -c | sort -rn | awk '{print $1, "subclasses of " $2}'
rg -o -N --no-filename -t ts 'function\s+([a-z]+)[A-Z]\w*' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2 {print $1, "functions named " $2 "*"}'
# TS8
rg -n -t ts '^(let|var)\s+\w+|getInstance\s*\(|static\s+#?_?instance\b|^export\s+(default\s+)?(const\s+\w+(\s*:\s*\w+)?\s*=\s*)?new\s' .
# TS9
for i in $(rg -o -N --no-filename -t ts '^\s*(?:export\s+)?interface\s+(\w+)' -r '$1' .); do echo "$i: $(rg -c -t ts "implements\s+([\w<>]+,\s*)*$i\b" . | awk -F: '{s+=$NF} END {print s+0}')"; done
# TS10
rg -n -t ts -U -P '(\w+)\s*\(([^)]*)\)[^{]*\{\s*return\s+this\.#?\w+\.\1\(\2\);?\s*\}' .
# TS11
rg -n -t ts 'Array\.isArray\(|\.(children|parts|items|nodes|contents)\b.*\.(map|forEach|reduce|flatMap)\(' .
# TS12
rg -n -t ts '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(' .
rg -n -t ts '\b[a-z]+_[a-z_]+\s*:|\*\s*100\b|/\s*100\b' .
rg -n -t ts "^\s*declare\s+(class|const|function)\s+\w+|^\s*import\s.+from\s+['\"][^./]" .
# TS13
rg -o -N --no-filename -t ts '(?:if\s*\(\s*!?|return\s+)(\w+\.\w+)\s*(?:\)|\?\s|[!=]==?\s*(?:null|undefined))' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -n -t ts '[!=]==?\s*(null|undefined)\b|\?\.|\?\?' .
# TS14
rg -n -t ts -U -P '(?:static\s+)?(?:create|make|build|new)\w*\s*\([^)]*\)[^{]*\{\s*return\s+new\s+\w+\([^)]*\);?\s*\}' .
# TS15
rg -o -N --no-filename -t ts '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t ts -P '(?<=\bcase )\x27[^\x27\n]{2,}\x27|(?<=[\w)\]])\[\s*\x27[^\x27\n]*\x27(*SKIP)(*F)|\x27[^\x27\n]*\x27(?=:[ \t]*[^\s/])(*SKIP)(*F)|\x27[^\x27\n]?\x27(*SKIP)(*F)|\x27[^\x27\n]{2,}\x27' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -n -t ts "\[\s*'[^']+'(\s*,\s*'[^']+'){2,}\s*\]|/\^[^/\n]+/" .
rg -o -N --no-filename -t ts '(?:[!=]==?|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# TS16
rg -n -t ts '^( {8,}|\t{4,})(\} )?(if|else|for|while|switch|try)\b' .
# TS17
rg -n -t ts -P '\b(fs\.\w+|(?<![.\w])fetch\((?![^)]*\)\s*[:{])|readFile|writeFile|\.query\(|process\.env|localStorage)' .
rg -c -t ts '^\s*(export\s+)?(async\s+)?(function\s+\w+|class\s+\w+|((public|private|protected|static|override)\s+)*#?\w+\s*\([^)]*\)[^{;=]*\{)' . | sort -t: -k2 -rn
# TS18
rg -n -t ts -i "throw new \w*Error\(['\"\`][^'\"\`]*(not supported|unsupported|not implemented|read-only|cannot be)" .
rg -n -t ts -P '^\s+(?:override\s+)?(?!if|for|while|switch|catch|constructor)\w+\s*\([^)]*\)[^{]*\{\s*\}' .
# TS19
rg -n -t ts -U -P '^\s*(?:export\s+)?interface\s+\w+[^{]*\{(?:[^{}]*?;){5,}[^{}]*\}' .
# TS20
rg -n -t ts -P 'new\s+\w*(Client|Pool|Connection|Database|Db|Gateway|Mailer|Smtp|Redis|Http|Api|Logger)\w*\(|new Date\(\)|Date\.now\(\)|performance\.now\(\)|\bset(Timeout|Interval)\(|(?<![.\w])fetch\((?![^)]*\)\s*[:{])|process\.env\b' .
rg -n -t ts '=\s*(new\s+)?[\w.]+\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# TS21
rg -n -t ts '\b(on|before|after|pre|post|will|did)[A-Z]\w*\??\s*[=:(,)]|\w+(\s*:\s*\w+)?\s*=\s*\{\}\s*[,)]' .
# TS22
rg -n -t ts -i '\b\w*(cache|memo)\w*\s*=\s*(new Map|\{\}|\[\])' .
# TS23
{ rg -U -o -N --no-filename -t ts -P '^\s*(?:export\s+)?interface\s+\w+[^{]*\{[^}]*\}' . | rg -o -N -P '^\s*(?:readonly\s+)?(\w+)\s*\??\s*[(:<]' -r 'B:$1'; rg -o -N --no-filename -t ts -P '\babstract\s+(?:(?:async|public|protected)\s+)*(\w+)\s*[(<]' -r 'B:$1' .; rg -o -N -H -t ts -P '^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s+)?(?:function\b|\([^)]*\)[^=]*=>|\w+\s*=>)|^\s*(?:(?:public|private|protected|static|async|get|set)\s+)*#?(?!(?:if|for|while|switch|catch|return|function)\b)(\w+)\s*(?:<[^>]*>)?\([^)]*\)[^{;=]*\{' -r '$1$2$3' . | sort -u; } | awk -F: '$1 == "B" {b[$2]; next} $NF !~ /^(constructor|main)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print ((n in b) ? 2 : (n ~ /^_/) ? 0 : 1), c[n], n ":" f[n] ((n in b) ? " (override)" : "")}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# TS24
{ d='^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s+)?(?:function\b|\([^)]*\)[^=]*=>|\w+\s*=>)|^\s*(?:(?:public|private|protected|static|async|get|set)\s+)*#?(?!(?:if|for|while|switch|catch|return|function)\b)(\w+)\s*(?:<[^>]*>)?\([^)]*\)[^{;=]*\{|^(?:export\s+)?(?:const|let|var)\s+(\w+)'; w='^\s*(?://|/\*|\*(?:\s|/|$)).*(*SKIP)(*F)|\w+'; g='!**/{node_modules,dist,build}/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t ts -P "$d" -r 'D $1$2$3$4' .; rg -n -H -t ts '' . | sed 's/^/L /'; rg -n -H -o -t ts -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t ts -g "$g" -P "$d" -r 'X $1$2$3$4' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(constructor|main)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# TS25
{ rg -n -H -o -t ts -P '^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)|^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s+)?(?:function\b|\([^)]*\)[^=]*=>|\w+\s*=>)|^\s*(?:(?:public|private|protected|static|async|get|set)\s+)*#?(?!(?:if|for|while|switch|catch|return|function)\b)(\w+)\s*(?:<[^>]*>)?\([^)]*\)[^{;=]*\{' -r 'D $1$2$3' .; rg -n -H -t ts '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

TS9 prints `Name: count`. A count of 1 is the hit; a count of 0 means the interface is used structurally, so search for the type name before calling it unused.

## Go

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| GO1 | `switch` on a kind/type/mode/status value or on a command word | a branch on a discriminator; count its cases and find every other branch on the same value | Strategy, State, Command, Factory Method |
| GO2 | type switches `.(type)` and type assertions | type dispatch over `any` or an interface | Visitor, Composite, Strategy |
| GO3 | `} else if` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| GO4 | `bool` parameters; boolean literal arguments | a flag that picks behaviour | Strategy, Decorator, Builder |
| GO5 | functions with 4+ parameters; calls passing several zero values | a long or optional-heavy parameter list | Builder (functional options), Builder - Introduce Parameter Object |
| GO6 | ranging over listener slices; state assignment followed by calls; 3+ consecutive collaborator calls | hand-rolled or hard-coded notification | Observer, Mediator |
| GO7 | function name prefix families | sibling bodies to compare for the same step order | Template Method, Strategy |
| GO8 | package-level `var`, `sync.Once`, `OnceValue` | shared or global mutable object | Singleton, KISS - Pattern overuse (singleton) |
| GO9 | interfaces and how many receivers implement their first method | an interface with exactly one implementation | KISS - Pattern overuse (one implementation) |
| GO10 | methods whose body is `return r.field.SameName(` | a pass-through wrapper when most methods of a type match | KISS - Needless indirection, Decorator, Proxy |
| GO11 | `[]any`, `[]interface{}`, `Children`/`Contents` fields | a tree held as untyped values | Composite, Visitor |
| GO12 | calls on a name ending in client, api, sdk, gateway or vendor | a foreign API shape converted at call sites | Adapter, Facade |
| GO13 | `nil` checks other than `err` | the same absence check repeated | Null Object |
| GO14 | `New`/`Make` functions returning an interface | a factory with nothing to decide when the interface has one implementation | KISS - Pattern overuse (one implementation) |
| GO15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| GO16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| GO17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| GO18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| GO19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| GO20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| GO21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| GO22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| GO23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| GO24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| GO25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# GO1
rg -n -t go '^\s*switch\b' .
rg -n -t go -i 'switch\s+[\w.]*((kind|type|mode|status|state|role|tier|action|format|method|cmd|command)\w*|\w+\[0\])\s*\{' .
# GO2
rg -n -t go '\.\(type\)|\.\(\*?[A-Z]\w*\)' .
# GO3
rg -n -t go '\}\s*else\s+if\b' .
# GO4
rg -U -o -n -t go 'func\s+(?:\([^)]*\)\s*)?(\w+)\s*\([^)]*?\b(\w+)\s+bool\b' -r 'func $1(... $2 bool ...)' .
rg -n -t go '\w\([^()]*\b(true|false)\s*,' .
# GO5
rg -U -o -n -H -t go -P 'func\s+(?:\([^)]*\)\s*)?(\w+)\s*(?:\[[^\]]*\])?\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)' -r '@@${1}@@${2}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t go '\w\([^()]*\b(nil|false|""|0)\s*,\s*(nil|false|""|0)\b' .
# GO6
rg -n -t go -i 'range\s+[\w.]*(listeners|subscribers|observers|handlers|callbacks|hooks)' .
rg -n -t go -A6 '\.(Status|State|status|state)\s*=[^=]' .
rg -n -t go -U '(\n\s*\w+\.\w+\.\w+\([^\n]*){3,}' .
# GO7
rg -o -N --no-filename -t go '^func\s+(?:\([^)]*\)\s*)?([a-z]+|[A-Z][a-z]+)[A-Z]\w*\(' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2'
# GO8
rg -n -t go '^var\s+\w+|sync\.Once|OnceValue|OnceFunc' .
# GO9
for m in $(rg -o -N --no-filename -t go -U '^type\s+\w+\s+interface\s*\{\s*(\w+)\(' -r '$1' .); do echo "$m: $(rg -c -t go "^func \(\w+ \*?\w+\) $m\(" . | awk -F: '{s+=$NF} END {print s+0}')"; done
# GO10
rg -n -t go -U -P 'func \(\w+ \*?\w+\) (\w+)\(([^)]*)\)[^{]*\{\s*return \w+\.\w+\.\1\(' .
# GO11
rg -n -t go '\[\](any|interface\{\})|\b(Children|Contents|Parts|Nodes|children|contents|parts|nodes)\s+\[\]' .
# GO12
rg -n -t go '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(' .
# GO13
rg -n -t go '[!=]= nil' . | rg -v '\berr\s*[!=]= nil'
# GO14
rg -n -t go 'func\s+(New|Make|Create)\w*\([^)]*\)\s+[A-Z]\w*\s*\{' .
# GO15
rg -o -N --no-filename -t go '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t go -P '(?<=\bcase )"[^"\n]{2,}"|(?:(?<=[\w)\]])\[\s*|:)"[^"\n]*"(*SKIP)(*F)|"[^"\n]*"(?=:[ \t]*[^\s/])(*SKIP)(*F)|"[^"\n]?"(*SKIP)(*F)|"[^"\n]{2,}"' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -o -N --no-filename -t go '(?:[!=]=|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# GO16
rg -n -t go '^\t{4,}(\} )?(if|else|for|switch|select)\b' .
# GO17
rg -n -t go '\b(os\.(Create|Open|OpenFile|ReadFile|WriteFile)|http\.\w+\(|sql\.\w+\(|json\.(Marshal|Unmarshal)|f\.Write\w*)' .
rg -c -t go '^func ' . | sort -t: -k2 -rn
# GO18
rg -n -t go -i 'panic\("[^"]*(not (implemented|supported)|unsupported)|errors\.New\("[^"]*(not supported|unsupported|not implemented)' .
rg -n -t go 'func \(\w+ \*?\w+\) \w+\([^)]*\)\s*(\w+\s*)?\{\s*\}' .
# GO19
rg -n -t go -U -P '^type\s+\w+\s+interface\s*\{(?:\s*\n\s*\w+\([^\n]*){5,}' .
# GO20
rg -n -t go '\b(sql\.Open|http\.(Get|Post|NewRequest)|http\.DefaultClient|&http\.Client\{|time\.(Now|Since|Until|Sleep|After|Tick)\(|os\.(Create|Open|OpenFile|ReadFile|WriteFile|Getenv|LookupEnv|Environ)\(|redis\.NewClient|smtp\.\w+\()' .
rg -n -t go '\w+\.New\w*\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# GO21
rg -n -t go '\b(On|Before|After|Pre|Post)[A-Z]\w*\b|func\s.*\(\s*_\s|,\s*_\s+\w+' .
# GO22
rg -n -t go -i '\b\w*(cache|memo)\w*\s*(=|:=)\s*(map\[|make\(map)' .
# GO23
{ rg -U -o -N --no-filename -t go -P 'type\s+\w+\s+interface\s*\{[^}]*\}' . | rg -o -N -P '^\s*([A-Za-z]\w*)\s*\(' -r 'B:$1'; rg -o -N -H -t go -P '^func\s+(?:\([^)]*\)\s*)?(\w+)' -r '$1' . | sort -u; } | awk -F: '$1 == "B" {b[$2]; next} $NF !~ /^(main|init|Error|String|ServeHTTP|Test.*|Benchmark.*|Example.*|Fuzz.*)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print ((n in b) ? 2 : (n ~ /^_/) ? 0 : 1), c[n], n ":" f[n] ((n in b) ? " (override)" : "")}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# GO24
{ d='^func\s+(?:\([^)]*\)\s*)?(\w+)|^(?:var|const)\s+(\w+)'; w='^\s*(?://|/\*).*(*SKIP)(*F)|\w+'; g='!**/vendor/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t go -P "$d" -r 'D $1$2' .; rg -n -H -t go '' . | sed 's/^/L /'; rg -n -H -o -t go -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t go -g "$g" -P "$d" -r 'X $1$2' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(_|main|init|Error|String|ServeHTTP|Test.*|Benchmark.*|Example.*|Fuzz.*)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# GO25
{ rg -n -H -o -t go -P '^func\s+(?:\([^)]*\)\s*)?(\w+)' -r 'D $1' .; rg -n -H -t go '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

GO9 prints `FirstMethod: count`. A count of 1 is the hit. Go idiom puts small interfaces where they are consumed, so an interface used by one consumer as a test seam is cleared only when a test double exists.

## Rust

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| RS1 | `match` on a kind/type/mode/status value or on a string `as_str()` | a branch on a discriminator; count its arms and find every other `match` on the same value | Strategy, State, Command, Factory Method |
| RS2 | `downcast`, `type_id`, `as_any`, `Any` | type dispatch through `dyn Any` | Visitor, Composite |
| RS3 | `} else if` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| RS4 | `bool` parameters; boolean literal arguments | a flag that picks behaviour | Strategy, Decorator, Builder |
| RS5 | functions with 4+ parameters; calls passing `None` placeholders | a long or optional-heavy parameter list | Builder, Builder - Introduce Parameter Object |
| RS6 | loops over listener vectors; state assignment followed by calls; 3+ consecutive `self.field.method(` calls | hand-rolled or hard-coded notification | Observer, Mediator |
| RS7 | function name prefix families | sibling bodies to compare for the same step order | Template Method, Strategy |
| RS8 | `static`, `OnceLock`, `LazyLock`, `lazy_static!`, `thread_local!` | shared or global object | Singleton, KISS - Pattern overuse (singleton) |
| RS9 | traits and their `impl Trait for` count | a trait with exactly one implementation | KISS - Pattern overuse (one implementation) |
| RS10 | methods whose body is `self.field.same_name(` | a pass-through wrapper when most methods of a type match | KISS - Needless indirection, Decorator, Proxy |
| RS11 | `Vec<Box<dyn ..>>`, `Box<Self>`, `children` fields | a tree or heterogeneous collection | Composite, Visitor |
| RS12 | calls on a name ending in client, api, sdk, gateway or vendor; `impl From` | a foreign API shape converted at call sites | Adapter |
| RS13 | `Option` checks grouped by expression | the same absence check repeated | Null Object |
| RS14 | a factory whose whole body is `Box::new(X ..)` | a factory with nothing to decide | KISS - Pattern overuse (one implementation) |
| RS15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| RS16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| RS17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| RS18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| RS19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| RS20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| RS21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| RS22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| RS23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| RS24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| RS25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# RS1
rg -n -t rust '\bmatch\s+' .
rg -n -t rust -i 'match\s+[\w.&*]*(kind|type|mode|status|state|role|tier|action|format|method|channel|cmd|command)\w*(\.as_str\(\))?\s*\{' .
# RS2
rg -n -t rust 'downcast(_ref|_mut)?|\.type_id\(\)|\bas_any\b|\bdyn Any\b' .
# RS3
rg -n -t rust '\}\s*else\s+if\b' .
# RS4
rg -U -o -n -t rust 'fn\s+(\w+)[^)]*?\b(\w+)\s*:\s*bool\b' -r 'fn $1(... $2: bool ...)' .
rg -n -t rust '\w\([^()]*\b(true|false)\s*[,)]' .
# RS5
rg -U -o -n -H -t rust -P 'fn\s+(\w+)\s*(?:<(?:[^<>]|<[^<>]*>)*>)?\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)' -r '@@${1}@@${2}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t rust '\bNone\s*,\s*(None|false|true)\b' .
# RS6
rg -n -t rust -i 'for\s+\w+\s+in\s+(&|&mut\s+)?(self\.)?\w*(listeners|subscribers|observers|handlers|callbacks|hooks)' .
rg -n -t rust -A6 '\.(status|state)\s*=[^=]' .
rg -n -t rust -U '(\n\s*self\.\w+\.\w+\([^\n]*){3,}' .
# RS7
rg -o -N --no-filename -t rust 'fn\s+([a-z]+)_\w+\s*[<(]' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2'
# RS8
rg -n -t rust '\bstatic\s+(mut\s+)?[A-Z_]+\s*:|OnceLock|LazyLock|lazy_static!|thread_local!' .
# RS9
for t in $(rg -o -N --no-filename -t rust '^\s*(?:pub(?:\([^)]*\))?\s+)?trait\s+(\w+)' -r '$1' .); do echo "$t: $(rg -c -t rust "impl(<[^>]*>)?\s+$t(<[^>]*>)?\s+for\b" . | awk -F: '{s+=$NF} END {print s+0}')"; done
# RS10
rg -n -t rust -U -P 'fn (\w+)\(&(?:mut )?self(?:,\s*)?([^)]*)\)[^{]*\{\s*self\.\w+\.\1\(' .
# RS11
rg -n -t rust 'Vec<Box<dyn|Box<Self>|Vec<Self>|\b(children|parts|contents|nodes)\s*:\s*(Vec|Option|Box)<' .
# RS12
rg -n -t rust '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(|impl\s+From<' .
# RS13
rg -o -N --no-filename -t rust '(?:match|if let Some\(\w+\) =)\s+&?([\w.]+)' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -n -t rust 'if let Some\(|\.is_some\(\)|\.is_none\(\)|None\s*=>' .
# RS14
rg -n -t rust -U -P 'fn (?:new|create|make)\w*\([^)]*\)\s*->\s*Box<dyn \w+>\s*\{\s*Box::new\(\w+' .
# RS15
rg -o -N --no-filename -t rust '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t rust -P '(?<=[\w)\]])\[\s*"[^"\n]*"(*SKIP)(*F)|"[^"\n]*"(?=:[ \t]*[^\s/])(*SKIP)(*F)|"[^"\n]?"(*SKIP)(*F)|"[^"\n]{2,}"' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -o -N --no-filename -t rust '(?:[!=]=|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# RS16
rg -n -t rust '^( {16,}|\t{4,})(\} )?(if|else|for|while|match|loop)\b' .
# RS17
rg -n -t rust '\b(std::fs|fs::\w+|File::(open|create)|reqwest|TcpStream|std::env|env::var)' .
rg -c -t rust '^\s*(pub(\([^)]*\))?\s+)?fn\s' . | sort -t: -k2 -rn
# RS18
rg -n -t rust 'unimplemented!|todo!|panic!\("[^"]*(not supported|unsupported|not implemented)|Err\(\w*Unsupported' .
# RS19
rg -n -t rust -U -P '^\s*(?:pub\s+)?trait\s+\w+[^{]*\{(?:[^{}]*?\bfn\s){5,}' .
# RS20
rg -n -t rust '\b\w*(Client|Pool|Connection|Mailer|Smtp\w*|Http\w*)::(new|connect|default|builder)\(|reqwest::|std::fs::|File::(open|create)\(|SystemTime::now\(|Instant::now\(|Utc::now\(|env::(var|var_os|vars)\(|thread::sleep\(|time::sleep\(' .
rg -n -t rust '::(new|connect|builder)\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# RS21
rg -n -t rust 'fn\s+\w+[^)]*\b_[a-z]\w*\s*:|\b(on|before|after|pre|post)_\w+\s*:' .
# RS22
rg -n -t rust -i '\w*(cache|memo)\w*\s*[:=]\s*(HashMap|BTreeMap)' .
# RS23
{ rg -U -o -N --no-filename -t rust -P '(?ms)^\s*(?:pub(?:\([^)]*\))?\s+)?trait\s+\w+[^{]*\{.*?^\}' . | rg -o -N -P '\bfn\s+(\w+)' -r 'B:$1'; rg -o -N -H -t rust -P '^\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:async|const|unsafe|extern)\s+)*fn\s+(\w+)' -r '$1' . | sort -u; } | awk -F: '$1 == "B" {b[$2]; next} $NF !~ /^(main|test_.*)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print ((n in b) ? 2 : (n ~ /^_/) ? 0 : 1), c[n], n ":" f[n] ((n in b) ? " (override)" : "")}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# RS24
{ d='^\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:async|const|unsafe|extern)\s+)*fn\s+(\w+)|^(?:pub(?:\([^)]*\))?\s+)?(?:static|const)\s+(?:mut\s+)?(?!fn\b)(\w+)'; w='^\s*(?://|/\*).*(*SKIP)(*F)|\w+'; g='!**/target/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t rust -P "$d" -r 'D $1$2' .; rg -n -H -t rust '' . | sed 's/^/L /'; rg -n -H -o -t rust -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t rust -g "$g" -P "$d" -r 'X $1$2' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(main|test_.*)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# RS25
{ rg -n -H -o -t rust -P '^\s*(?:pub(?:\([^)]*\))?\s+)?(?:(?:async|const|unsafe|extern)\s+)*fn\s+(\w+)' -r 'D $1' .; rg -n -H -t rust '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

RS9 prints `Trait: count`. A count of 1 is the hit unless the trait exists for a generic bound that tests or another crate fill.

## Kotlin

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| KT1 | `when` on a kind/type/mode/status value or on a command word | a branch on a discriminator; count its branches and find every other `when` on the same value | Strategy, State, Command, Factory Method |
| KT2 | `is` and `as?` checks | type dispatch; a `when` full of `is` branches is the hit | Visitor, Composite, Strategy |
| KT3 | `} else if` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| KT4 | `Boolean` parameters and properties | a flag that picks behaviour | Strategy, Decorator, Builder |
| KT5 | constructors and functions with 4+ parameters (multi-line too); `null` placeholders | a long or optional-heavy parameter list | Builder (named and default arguments), Builder - Introduce Parameter Object |
| KT6 | loops over listener lists; state assignment followed by calls | hand-rolled or hard-coded notification | Observer, Mediator |
| KT7 | subclass counts per base; class name suffix families | sibling bodies to compare for the same step order | Template Method, Strategy, Factory Method |
| KT8 | `object` declarations, `companion object`, `by lazy`, top-level `var` | shared or global mutable object | Singleton, KISS - Pattern overuse (singleton) |
| KT9 | interfaces and how many classes list them as a supertype | an interface with exactly one implementation | KISS - Pattern overuse (one implementation) |
| KT10 | functions whose body is `x.sameName(` | a pass-through wrapper when most functions of a class match | KISS - Needless indirection, Decorator, Proxy |
| KT11 | `List<Any>`, `children` fields, sealed hierarchies | a tree or closed set walked by type | Composite, Visitor |
| KT12 | calls on a name ending in client, api, sdk, gateway or vendor; the same call wrapped in a parse at several sites | a foreign API shape converted at call sites | Adapter |
| KT13 | `null` checks, `?.`, `?:` | the same absence check repeated | Null Object |
| KT14 | a factory function whose whole body is a constructor call | a factory with nothing to decide | KISS - Pattern overuse (one implementation) |
| KT15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| KT16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| KT17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| KT18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| KT19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| KT20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| KT21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| KT22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| KT23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| KT24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| KT25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# KT1
rg -n -t kotlin '\bwhen\s*\(' .
rg -n -t kotlin -i 'when\s*\([^)]*((kind|type|mode|status|state|role|tier|action|format|method|cmd|command)\w*|\w+\[0\])[^)]*\)' .
# KT2
rg -n -t kotlin '(\bis|!is)\s+[A-Z]\w*|\bas\?\s' .
# KT3
rg -n -t kotlin '\}\s*else\s+if\b' .
# KT4
rg -n -t kotlin '\w+\s*:\s*Boolean\b' .
# KT5
rg -U -o -n -H -t kotlin -P '(?:fun\s+(?:<[^>]*>\s*)?(?:[\w.]+\.)?(\w+)|class\s+(\w+)(?:<[^>]*>)?|(constructor))\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)' -r '@@${1}${2}${3}@@${4}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t kotlin '\bnull\s*,\s*(null|false|true)\b' .
# KT6
rg -n -t kotlin -i '(listeners|subscribers|observers|handlers|callbacks)\w*\.forEach|for\s*\(\w+\s+in\s+\w*(listeners|subscribers|observers|handlers|callbacks)' .
rg -n -t kotlin -A6 '\b(status|state)\s*=[^=]' .
# KT7
rg -o -N --no-filename -t kotlin 'class\s+\w+[^{]*?:\s*(\w+)\(' -r '$1' . | sort | uniq -c | sort -rn | awk '{print $1, "subclasses of " $2}'
rg -o -N --no-filename -t kotlin 'class\s+[A-Z][a-z]+([A-Z]\w*)' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2 {print $1, "classes named *" $2}'
# KT8
rg -n -t kotlin '^\s*object\s+\w+|companion\s+object|by\s+lazy|^(private\s+|internal\s+)?var\s+\w+' .
# KT9
for i in $(rg -o -N --no-filename -t kotlin '^\s*(?:(?:fun|sealed|private|internal|public)\s+)*interface\s+(\w+)' -r '$1' .); do echo "$i: $(rg -c -t kotlin "(class|object)\s+\w+[^{]*[:,]\s*$i\b" . | awk -F: '{s+=$NF} END {print s+0}')"; done
# KT10
rg -n -t kotlin -U -P 'fun (\w+)\(([^)]*)\)[^={]*(?:=\s*|\{\s*return\s+)\w+\.\1\(' .
# KT11
rg -n -t kotlin 'List<Any>|\b(children|parts|contents|nodes)\s*:\s*(Mutable)?List<|sealed\s+(class|interface)' .
# KT12
rg -n -t kotlin '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(' .
rg -o -N --no-filename -t kotlin '(\w+\.\w+)\([^()]*\)\.to(?:Double|Int|Long|BigDecimal)\(\)' -r '$1' . | sort | uniq -c | sort -rn
# KT13
rg -n -t kotlin '[!=]=\s*null|\?\.|\?:' .
# KT14
rg -n -t kotlin -U -P 'fun (?:create|make|build|new)\w*\([^)]*\)\s*(?::\s*\w+\s*)?(?:=\s*|\{\s*return\s+)[A-Z]\w*\(' .
# KT15
rg -o -N --no-filename -t kotlin '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t kotlin -P '(?<=[\w)\]])\[\s*"[^"\n$]*"(*SKIP)(*F)|"[^"\n$]*"(?=:[ \t]*[^\s/])(*SKIP)(*F)|"[^"\n$]?"(*SKIP)(*F)|"[^"\n$]{2,}"' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -o -N --no-filename -t kotlin '(?:[!=]=|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# KT16
rg -n -t kotlin -P '^( {16,}|\t{4,})(\} )?(?!else\s*->)(if|else|for|while|when|try)\b.*\{\s*$' .
# KT17
rg -n -t kotlin '\b(File\(|Files\.|URL\(|HttpClient|System\.getenv|readText\(|writeText\()' .
rg -c -t kotlin '^\s*((override|open|private|internal|public|suspend)\s+)*fun\s' . | sort -t: -k2 -rn
# KT18
rg -n -t kotlin 'UnsupportedOperationException|NotImplementedError|\bTODO\(|error\("[^"]*(not supported|unsupported|cannot be)' .
rg -n -t kotlin 'override fun \w+\([^)]*\)\s*(:\s*\w+\s*)?\{\s*\}' .
# KT19
rg -n -t kotlin -U -P '^\s*(?:\w+\s+)*interface\s+\w+[^{]*\{(?:[^{}]*?\b(?:fun|val|var)\s){5,}' .
# KT20
rg -n -t kotlin '(=|\()\s*\w*(Client|Gateway|Mailer|Database|Dao|HttpClient|Smtp\w*)\(|System\.(currentTimeMillis|nanoTime|getenv|getProperty)|(LocalDate|LocalDateTime|Instant)\.now\(|Thread\.sleep\(|\bdelay\(' .
rg -n -t kotlin '=\s*[\w.]+\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# KT21
rg -n -t kotlin '\b(on|before|after|pre|post)[A-Z]\w*\s*:|\)\s*->\s*\w+\)\?\s*=\s*null' .
# KT22
rg -n -t kotlin -i '\w*(cache|memo)\w*\s*=\s*(mutableMapOf|HashMap|ConcurrentHashMap)' .
# KT23
rg -o -N -H -t kotlin -P '^\s*(?:(?:private|internal|public|protected|suspend|inline|operator|infix|open|abstract|final|tailrec)\s+)*fun\s+(?:<[^>]*>\s*)?(?:[\w.]+\.)?(\w+)\s*\(' -r '$1' . | sort -u | awk -F: '$NF !~ /^(main)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print (n ~ /^_/ ? 0 : 1), c[n], n ":" f[n]}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# KT24
{ d='^\s*(?:(?:private|internal|public|protected|suspend|inline|operator|infix|open|abstract|final|tailrec)\s+)*fun\s+(?:<[^>]*>\s*)?(?:[\w.]+\.)?(\w+)\s*\(|^(?:(?:private|internal|public)\s+)?(?:const\s+)?(?:val|var)\s+(\w+)'; w='^\s*(?://|/\*|\*(?:\s|/|$)).*(*SKIP)(*F)|\w+'; g='!**/{build,.gradle}/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t kotlin -P "$d" -r 'D $1$2' .; rg -n -H -t kotlin '' . | sed 's/^/L /'; rg -n -H -o -t kotlin -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t kotlin -g "$g" -P "$d" -r 'X $1$2' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(main)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# KT25
{ rg -n -H -o -t kotlin -P '^\s*(?:(?:private|internal|public|protected|suspend|inline|operator|infix|open|abstract|final|tailrec)\s+)*fun\s+(?:<[^>]*>\s*)?(?:[\w.]+\.)?(\w+)\s*\(' -r 'D $1' .; rg -n -H -t kotlin '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

KT9 prints `Name: count`. A count of 1 is the hit. A `fun interface` taking lambdas at call sites is cleared, since the lambdas are the other implementations.

## Swift

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| SW1 | `switch` on a kind/type/mode/status value | a branch on a discriminator; count its cases and find every other `switch` on the same value | Strategy, State, Command, Factory Method |
| SW2 | `as?`, `as!`, `is` checks | type dispatch; a chain over one value is the hit | Visitor, Composite, Strategy |
| SW3 | `} else if` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| SW4 | `Bool` parameters and stored `Bool` flags | a flag that picks or adds behaviour | Strategy, Decorator, Builder |
| SW5 | `init` or functions with 4+ parameters (multi-line too); `nil` placeholders | a long or optional-heavy parameter list | Builder (default arguments), Builder - Introduce Parameter Object |
| SW6 | loops over observer lists; `didSet`/`willSet` bodies | hand-rolled or hard-coded notification | Observer, Mediator |
| SW7 | type name suffix families; function name prefix families | sibling bodies to compare for the same step order | Template Method, Strategy, Factory Method |
| SW8 | `static let shared`, `static var`, top-level `var` | shared or global mutable object | Singleton, KISS - Pattern overuse (singleton) |
| SW9 | protocols and how many types conform | a protocol with exactly one conformer | KISS - Pattern overuse (one implementation) |
| SW10 | functions whose body is `x.sameName(` | a pass-through wrapper when most functions of a type match | KISS - Needless indirection, Decorator, Proxy |
| SW11 | `[Any]`, `[any P]`, `indirect enum`, `children` | a tree or heterogeneous collection | Composite, Visitor |
| SW12 | calls on a name ending in client, api, sdk, gateway or vendor | a foreign API shape converted at call sites | Adapter |
| SW13 | `nil` checks, `if let`, `guard let`, `??` | the same absence check repeated | Null Object |
| SW14 | a `static func make...` whose whole body is the initializer of its return type | a factory with nothing to decide | KISS - Pattern overuse (one implementation) |
| SW15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| SW16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| SW17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| SW18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| SW19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| SW20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| SW21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| SW22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| SW23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| SW24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| SW25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# SW1
rg -n -t swift '^\s*switch\b' .
rg -n -t swift -i 'switch\s+[\w.]*(kind|type|mode|status|state|role|tier|action|format|method|cmd|command)\w*\s*\{' .
# SW2
rg -n -t swift '\bas[?!]\s|\bis\s+[A-Z]\w*' .
# SW3
rg -n -t swift '\}\s*else\s+if\b' .
# SW4
rg -n -t swift '\w+\s*:\s*Bool\b|\bvar\s+\w+\s*=\s*(true|false)\b' .
# SW5
rg -U -o -n -H -t swift -P '(?:func\s+(\w+)\s*(?:<[^>]*>)?|(?<![.\w])(init)[?!]?)\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)' -r '@@${1}${2}@@${3}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t swift '\b(nil|false)\s*,\s*(nil|false)\b' .
# SW6
rg -n -t swift -i '(observers|listeners|subscribers|handlers|callbacks)\w*\.forEach|for\s+\w+\s+in\s+\w*(observers|listeners|subscribers|handlers|callbacks)' .
rg -n -t swift -A6 'didSet\s*\{|willSet\s*\{' .
# SW7
rg -o -N --no-filename -t swift '(?:class|struct|enum)\s+[A-Z][a-z]+([A-Z]\w*)' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2 {print $1, "types named *" $2}'
rg -o -N --no-filename -t swift 'func\s+([a-z]+)[A-Z]\w*' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2 {print $1, "functions named " $2 "*"}'
# SW8
rg -n -t swift 'static\s+(let|var)\s+shared\b|static\s+var\s+\w+|^(nonisolated\(unsafe\)\s+)?var\s+\w+' .
# SW9
for p in $(rg -o -N --no-filename -t swift '^\s*(?:public\s+|internal\s+)?protocol\s+(\w+)' -r '$1' .); do echo "$p: $(rg -c -t swift "(class|struct|enum|actor|extension)\s+\w+\s*:[^{]*\b$p\b" . | awk -F: '{s+=$NF} END {print s+0}')"; done
# SW10
rg -n -t swift -U -P 'func (\w+)\(([^)]*)\)[^{]*\{\s*(?:return\s+)?\w+\.\1\(' .
# SW11
rg -n -t swift '\[Any\]|\[any \w+\]|indirect\s+enum|\b(children|parts|contents|nodes)\s*:\s*\[' .
# SW12
rg -n -t swift '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(' .
# SW13
rg -n -t swift '[!=]= nil|\bif let\b|\bguard let\b|\?\?' .
# SW14
rg -n -t swift -U -P 'static func (?:make|create|build|new)\w*\([^)]*\)\s*->\s*(\w+)\s*\{\s*(?:return\s+)?\1\(' .
# SW15
rg -o -N --no-filename -t swift '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t swift -P '(?<=\bcase )"[^"\n\\]{2,}"|(?<=[\w)\]])\[\s*"[^"\n\\]*"(*SKIP)(*F)|"[^"\n\\]*"(?=:[ \t]*[^\s/])(*SKIP)(*F)|"[^"\n\\]?"(*SKIP)(*F)|"[^"\n\\]{2,}"' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -o -N --no-filename -t swift '(?:[!=]=|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# SW16
rg -n -t swift '^( {16,}|\t{4,})(\} )?(if|else|for|while|switch|guard|do)\b' .
# SW17
rg -n -t swift '\b(FileManager|URLSession|UserDefaults|Data\(contentsOf|write\(to|ProcessInfo)' .
rg -c -t swift '^\s*((mutating|static|private|fileprivate|override|public|final)\s+)*func\s' . | sort -t: -k2 -rn
# SW18
rg -n -t swift 'fatalError\(|preconditionFailure\("[^"]*(not supported|unsupported|read-only)' .
rg -n -t swift '(override\s+)?func \w+\([^)]*\)\s*\{\s*\}' .
# SW19
rg -n -t swift -U -P '^\s*(?:public\s+)?protocol\s+\w+[^{]*\{(?:[^{}]*?\b(?:func|var)\s){5,}' .
# SW20
rg -n -t swift '(let|var)\s+\w+\s*=\s*\w*(Client|Gateway|Session|Database|Api|Repository|Mailer)\(|URLSession\.shared|UserDefaults\.standard|FileManager\.default|\bDate\(\)|Date\.now\b|ProcessInfo\.processInfo\.environment|Thread\.sleep|Task\.sleep|\bu?sleep\(' .
rg -n -t swift '=\s*[\w.]+\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# SW21
rg -n -t swift '\b(on|before|after|will|did)[A-Z]\w*\s*:\s*(@escaping\s*)?\(' .
# SW22
rg -n -t swift -i '\w*(cache|memo)\w*\s*:\s*\[[^\]]+:[^\]]+\]\s*=|\w*(cache|memo)\w*\s*=\s*\[\w+\s*:\s*\w+\]\(\)' .
# SW23
{ rg -U -o -N --no-filename -t swift -P '^\s*(?:public\s+)?protocol\s+\w+[^{]*\{[^}]*\}' . | rg -o -N -P '\bfunc\s+(\w+)' -r 'B:$1'; rg -o -N -H -t swift -P '^\s*(?:(?:private|fileprivate|internal|public|open|static|class|mutating|final|@\w+)\s+)*func\s+(\w+)' -r '$1' . | sort -u; } | awk -F: '$1 == "B" {b[$2]; next} $NF !~ /^(main|test.*)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print ((n in b) ? 2 : (n ~ /^_/) ? 0 : 1), c[n], n ":" f[n] ((n in b) ? " (override)" : "")}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# SW24
{ d='^\s*(?:(?:private|fileprivate|internal|public|open|static|class|mutating|final|@\w+)\s+)*func\s+(\w+)|^(?:(?:private|fileprivate|internal|public)\s+)?(?:let|var)\s+(\w+)'; w='^\s*(?://|/\*).*(*SKIP)(*F)|\w+'; g='!**/.build/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t swift -P "$d" -r 'D $1$2' .; rg -n -H -t swift '' . | sed 's/^/L /'; rg -n -H -o -t swift -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t swift -g "$g" -P "$d" -r 'X $1$2' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(main|test.*)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# SW25
{ rg -n -H -o -t swift -P '^\s*(?:(?:private|fileprivate|internal|public|open|static|class|mutating|final|@\w+)\s+)*func\s+(\w+)' -r 'D $1' .; rg -n -H -t swift '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

SW9 prints `Protocol: count`. A count of 1 is the hit unless a test target supplies the second conformer.

## Python

| ID | Signal | A hit means | Feeds |
|---|---|---|---|
| PY1 | `match`, and `if`/`elif` comparing a kind/type/mode/status field | a branch on a discriminator; count its cases and find every other branch on the same field | Strategy, State, Command, Factory Method |
| PY2 | `isinstance` and `type(x) is` checks, `isinstance(x, list)` included | type dispatch; a chain over one value is the hit | Visitor, Composite, Strategy |
| PY3 | `elif` | three or more in one function on the same variable form a chain | Strategy, State, Chain of Responsibility |
| PY4 | `bool` parameters and boolean defaults; boolean literal arguments | a flag that picks behaviour | Strategy, Decorator, Builder |
| PY5 | `def` with 4+ parameters after `self` (multi-line too); `None` placeholders | a long or optional-heavy parameter list | Builder (keyword arguments, dataclass), Builder - Introduce Parameter Object |
| PY6 | loops over listener lists; state assignment followed by calls | hand-rolled or hard-coded notification | Observer, Mediator |
| PY7 | class name suffix families; subclass counts per base | sibling bodies to compare for the same step order | Template Method, Strategy, Factory Method |
| PY8 | `_instance`, `__new__`, module-level instances (private classes too), `@cache`, `global` | shared or global mutable object | Singleton, KISS - Pattern overuse (singleton) |
| PY9 | `ABC`/`Protocol` classes and their subclass count | an abstraction with exactly one implementation | KISS - Pattern overuse (one implementation) |
| PY10 | methods whose body is `return self.x.same_name(` | a pass-through wrapper when most methods of a class match | KISS - Needless indirection, Decorator, Proxy |
| PY11 | `children`, `parts`, `contents` or `nodes` outside comments and docstring lines (PY2 holds the `isinstance` checks) | one/many distinction or a tree walked by hand | Composite, Visitor |
| PY12 | calls on a name ending in client, api, sdk, gateway or vendor | a foreign API shape converted at call sites | Adapter |
| PY13 | `is None` / `is not None` grouped by expression | the same absence check repeated | Null Object |
| PY14 | a factory whose whole body is `return SomeClass(...)` | a factory with nothing to decide | KISS - Pattern overuse (one implementation) |
| PY15 | repeated numeric and string literals, inline lists, regexes, and numbers used in comparisons | the same fact written in several places, or a coincidence; read both uses | DRY - Duplicated knowledge, DRY - Magic values, DRY - Duplicated logic across layers, DRY - Duplicate code inside one function |
| PY16 | control statements four or more levels deep | arrow code; a run of hits in one function is the hit | KISS - Nested conditionals |
| PY17 | I/O, environment or output calls; definition and import counts per file | a unit that mixes I/O with rules or formatting, or a file that every change touches | SOLID - SRP |
| PY18 | overrides or implementations that throw "not supported", stub, or do nothing | a subtype that breaks its parent's contract, or a fat interface forcing stubs | SOLID - LSP, SOLID - ISP |
| PY19 | interfaces, traits or protocols with 5 or more members | a wide contract; check which members each client uses | SOLID - ISP |
| PY20 | concrete infrastructure (clients, files, clocks, sleeps, environment) created inside code, and clients built with credentials | policy that builds its own dependencies; hits in a composition root or `main` are fine | SOLID - DIP |
| PY21 | hook-shaped names, defaulted option bags, underscore-prefixed parameters | a parameter or hook nothing passes or reads; check every caller | KISS - Speculative generality |
| PY22 | hand-rolled caches and memo tables | an optimization with no measurement; check the key and invalidation | KISS - Premature optimization |
| PY23 | function and method names defined in more than one file, private names first | copies that may already disagree: the strongest drift signal; diff the bodies | DRY - Duplicated knowledge |
| PY24 | functions, methods and top-level constants that no code outside dead code uses, and copies their own file never uses | a dead-code candidate; search for dynamic references before calling it dead | KISS - Dead code |
| PY25 | functions longer than 80 lines | a long function; split it by reason to change | KISS or SRP - Long function |

```sh
rg() { command rg ${RG_EXCLUDE:+-g "!$RG_EXCLUDE"} "$@"; }
# PY1
rg -n -t py '^\s*match\s+.+:\s*$' .
rg -n -t py -i '^\s*(el)?if\s+[\w.]*(kind|type|mode|status|state|role|tier|action|format|method|region|category|cmd|command)\w*\s*(==|in)\s' .
# PY2
rg -n -t py 'isinstance\(|type\(\w+\)\s*(is|==)' .
# PY3
rg -n -t py '^\s*elif\b' .
# PY4
rg -U -o -n -t py 'def\s+(\w+)\s*\([^)]*?\b(\w+)\s*(?::\s*bool\b|(?::[^,)=]*)?=\s*(?:True|False)\b)' -r 'def $1(... $2 ...)' .
rg -n -t py -P '^(?!\s*@).*\w\([^()]*\b(True|False)\s*[,)]' .
# PY5
rg -U -o -n -H -t py -P 'def\s+(\w+)\s*\(((?:[^()]|\((?:[^()]|\([^()]*\))*\))*)\)' -r '@@${1}@@${2}' . | awk -f "$SKILL_DIR/scripts/params.awk"
rg -n -t py '\bNone\s*,\s*(None|False|True)\b' .
# PY6
rg -n -t py -i 'for\s+\w+\s+in\s+(self\.)?_?\w*(listeners|subscribers|observers|handlers|callbacks|hooks)' .
rg -n -t py -A6 '\.(status|state)\s*=[^=]' .
# PY7
rg -o -N --no-filename -t py '^class\s+[A-Z][a-z]+([A-Z]\w*)' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2 {print $1, "classes named *" $2}'
rg -o -N --no-filename -t py '^class\s+\w+\((\w+)\)' -r '$1' . | sort | uniq -c | sort -rn | awk '{print $1, "subclasses of " $2}'
# PY8
rg -n -t py '_instance\b|def __new__|^[a-z_][a-z0-9_]*\s*=\s*_*[A-Z]\w*\(|@(functools\.)?(cache|lru_cache)\b|^\s*global\s+\w+' .
# PY9
for c in $(rg -o -N --no-filename -t py '^class\s+(\w+)\((?:\w+\.)?(?:ABC|Protocol)\b' -r '$1' .); do echo "$c: $(rg -c -t py "^class\s+\w+\([^)]*\b$c\b" . | awk -F: '{s+=$NF} END {print s+0}')"; done
# PY10
rg -n -t py -U -P 'def (\w+)\(self(?:,\s*)?([^)]*)\)[^:]*:\s*\n\s*return self\.\w+\.\1\(' .
# PY11
rg -n -t py -P '^(?!\s*(?:\"\"\"|\x27\x27\x27))[^#\n]*\b(children|parts|contents|nodes)\b' .
# PY12
rg -n -t py -P '\b(?:\w*_)?(?i:client|sdk|api|gateway|vendor)\.(?!(?:get|items|keys|values|pop|setdefault|update|copy)\()\w+\(|\b\w*[a-z0-9](?:Client|Sdk|SDK|Api|API|Gateway|Vendor)\.\w+\(' .
# PY13
rg -o -N --no-filename -t py '([\w.]+) is (?:not )?None' -r '$1' . | sort | uniq -c | sort -rn | awk '$1 > 2'
# PY14
rg -n -t py -U -P 'def (?:create|make|build|new)\w*\([^)]*\)[^:]*:\s*\n\s*return [A-Z]\w*\(' .
# PY15
rg -o -N --no-filename -t py '\b(?:\d+\.\d+|\d[\d_]{1,})\b' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
rg -o -N --no-filename -t py -P '(?<=\bcase )(?:"[^"\n]{2,}"|\x27[^\x27\n]{2,}\x27)|(?:(?<=[\w)\]])\[\s*|\.get\()(?:"[^"\n]*"|\x27[^\x27\n]*\x27)(*SKIP)(*F)|(?:"[^"\n]*"|\x27[^\x27\n]*\x27)(?=:[ \t]*[^\s#])(*SKIP)(*F)|(?:"[^"\n]?"|\x27[^\x27\n]?\x27)(*SKIP)(*F)|"[^"\n]{2,}"|\x27[^\x27\n]{2,}\x27' . | sort | uniq -c | sort -rn | awk '$1 > 2'
rg -o -N --no-filename -t py '(?:[!=]=|[<>]=?)\s*(\d[\d_.]*)\b' -r '$1' . | tr -d _ | sort | uniq -c | sort -rn | awk '$1 > 1'
# PY16
rg -n -t py '^( {16,}|\t{4,})((if|elif|for|while|with)\b.*[:(\[\\]|(else|try)\s*:)\s*(#.*)?$' .
# PY17
rg -n -t py '\b(open\(|requests\.\w+|sqlite3\.|smtplib\.|os\.environ|json\.dump|urllib\.request)' .
rg -c -t py '^\s*(async\s+)?def\s' . | sort -t: -k2 -rn
# PY18
rg -n -t py 'raise NotImplementedError|raise \w*(Unsupported|NotSupported)\w*' .
rg -n -t py -U -P 'def \w+\(self[^)]*\)[^:\n]*:\s*\n\s+(pass|\.\.\.)\s*$' .
# PY19
rg -c -t py '@abstractmethod|def \w+\(self[^)]*\)[^:]*:\s*\.\.\.\s*$' . | sort -t: -k2 -rn
# PY20
rg -n -t py '=\s*\w*(Client|Session|Connection|Gateway|Repository|Mailer|SMTP|Database|Api)\(|requests\.(get|post|put|delete)\(|sqlite3\.connect|smtplib\.|datetime\.(now|today|utcnow)\(|date\.today\(|time\.(time|monotonic|perf_counter|sleep)\(|os\.(environ|getenv\()' .
rg -n -t py '^\w+\s*=\s*[\w.]+\(.*\b(?i:api_?key|api_?secret|secret|token|password)\b' .
# PY21
rg -n -t py 'def \w+\([^)]*\b(on|before|after|pre|post)_\w+|\*\*kwargs|def \w+\([^)]*\b\w+\s*(:\s*[\w\[\], |]+)?=\s*None' .
# PY22
rg -n -t py -i '\w*(cache|memo)\w*\s*(:\s*[\w\[\], ]+)?=\s*(\{\}|dict\(\))|@(functools\.)?(lru_cache|cache)\b' .
# PY23
{ rg -U -o -N --no-filename -t py -P '^class\s+\w+\([^)]*\b(?:ABC|ABCMeta|Protocol)\b[^)]*\):\n(?:(?:[ \t][^\n]*)?\n)*' . | rg -o -N -P '^\s+(?:async\s+)?def\s+(\w+)' -r 'B:$1'; rg -o -N -H -t py -P '^\s*(?:async\s+)?def\s+(\w+)' -r '$1' . | sort -u; } | awk -F: '$1 == "B" {b[$2]; next} $NF !~ /^(__.*__|test_.*)$/ {c[$NF]++; f[$NF] = f[$NF] " " substr($0, 1, length($0) - length($NF) - 1)} END {for (n in c) if (c[n] > 1) print ((n in b) ? 2 : (n ~ /^_/) ? 0 : 1), c[n], n ":" f[n] ((n in b) ? " (override)" : "")}' | sort -k1,1n -k2,2nr | cut -d' ' -f2-
# PY24
{ d='^\s*(?:async\s+)?def\s+(\w+)|^([A-Za-z_]\w*)\s*(?::[^=\n]*)?=(?!=)'; w='^\s*(?:#|"""|'"'''"').*(*SKIP)(*F)|\w+'; g='!**/__pycache__/**'; r=$(cd "${REPO_ROOT:-.}" && pwd); rg -n -H -o -t py -P "$d" -r 'D $1$2' .; rg -n -H -t py '' . | sed 's/^/L /'; rg -n -H -o -t py -P "$w" -r 'W$0' .; echo "ROOT:$r"; command rg -n -H -o -t py -g "$g" -P "$d" -r 'X $1$2' "$r"; command rg -H -o -N -g "$g" -P "$w" -r 'R$0' "$r" | LC_ALL=C sort | uniq -c; } | awk -v here="$PWD" -v skip='^(__.*__|test_.*)$' -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/dead.awk" | sort
# PY25
{ rg -n -H -o -t py -P '^\s*(?:async\s+)?def\s+(\w+)' -r 'D $1' .; rg -n -H -t py '' . | sed 's/^/L /'; } | awk -f "$SKILL_DIR/scripts/ranges.awk" -f "$SKILL_DIR/scripts/long.awk" | sort -t'(' -k2 -rn
```

PY9 prints `Name: count`. A count of 1 is the hit. A `Protocol` may have no subclasses at all because conformance is structural, so search for the name in annotations before calling it unused.
