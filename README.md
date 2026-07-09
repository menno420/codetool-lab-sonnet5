# codetool-lab-sonnet5

Throwaway EAP capability-evaluation repo — the Sonnet 5 arm of a two-arm model-comparison experiment. Task: design and ship a real, general-purpose, open-source-quality CLI tool or library solving a genuine problem — tests, docs, CI, published — deliberately unrelated to SuperBot so there's no borrowed scaffolding. The tool itself and all its docs live in this repo; fleet coordination lives in control/.

The shipped tool is **cfgdiff**, documented below.

---

# cfgdiff

A cross-format **semantic config diff/convert CLI**. It parses JSON, YAML, TOML, INI, and
`.env` files into one normalized tree, then diffs them semantically (key order, formatting,
and comments never produce a diff -- only actual structural/value differences do) and can
convert between formats. Diffs and converts work **across formats**: compare `config.yaml`
against `config.toml` directly.

Python 3.10+.

## Install

Not yet on PyPI (see [Status](#status) below). Until then, install straight from GitHub:

```bash
pipx install git+https://github.com/menno420/codetool-lab-sonnet5
```

Once published to PyPI:

```bash
pipx install cfgdiff
```

## Quickstart

```bash
cfgdiff diff config.yaml config.toml          # semantic diff, human-readable
cfgdiff diff config.yaml config.toml --output json   # machine-readable
cfgdiff convert config.yaml --to json          # re-emit in another format
cfgdiff validate config.yaml                   # parse-check, exit 0/2
```

## Real example

Given `config.yaml`:

```yaml
server:
  host: localhost
  port: 8080
  debug: true
  allowed_ips:
    - 127.0.0.1
    - 10.0.0.1
database:
  name: myapp_db
  pool_size: 5
```

and `config.toml`:

```toml
[server]
host = "0.0.0.0"
port = 8080
debug = true
allowed_ips = ["127.0.0.1", "10.0.0.2"]

[database]
name = "myapp_db"
pool_size = "5"
```

```
$ cfgdiff diff config.yaml config.toml --no-color
~ database.pool_size: 5 (int) -> "5" (str) [type changed]
~ server.allowed_ips[1]: "10.0.0.1" -> "10.0.0.2"
~ server.host: "localhost" -> "0.0.0.0"
```

Exit code is `1` (differences found). Colorized output (added=green, removed=red,
changed=yellow) is the default when stdout is a terminal; `--no-color` or piping disables it.

`--output json`:

```
$ cfgdiff diff config.yaml config.toml --output json
[
  {
    "path": "database.pool_size",
    "kind": "type_changed",
    "old": 5,
    "new": "5"
  },
  {
    "path": "server.allowed_ips[1]",
    "kind": "value_changed",
    "old": "10.0.0.1",
    "new": "10.0.0.2"
  },
  {
    "path": "server.host",
    "kind": "value_changed",
    "old": "localhost",
    "new": "0.0.0.0"
  }
]
```

Ignore a noisy path (repeatable, dotted-path prefix match):

```
$ cfgdiff diff config.yaml config.toml --ignore server.allowed_ips --no-color
~ database.pool_size: 5 (int) -> "5" (str) [type changed]
~ server.host: "localhost" -> "0.0.0.0"
```

Convert to another format:

```
$ cfgdiff convert config.yaml --to json
{
  "server": {
    "host": "localhost",
    "port": 8080,
    "debug": true,
    "allowed_ips": [
      "127.0.0.1",
      "10.0.0.1"
    ]
  },
  "database": {
    "name": "myapp_db",
    "pool_size": 5
  }
}
```

Validate:

```
$ cfgdiff validate config.yaml
OK: config.yaml (yaml)

$ cfgdiff validate config.toml
OK: config.toml (toml)

$ echo '{"a": [1, 2,]}' > broken.json
$ cfgdiff validate broken.json
cfgdiff: error: broken.json:1:13: Expecting value
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | `diff`: files are semantically identical. `convert`/`validate`: succeeded. |
| `1`  | `diff`: differences were found. |
| `2`  | Error: file not found, unrecognized extension, parse failure, or an unrepresentable conversion (e.g. a `null` value converted to TOML). |

## Design & policies (read this if a diff surprises you)

* **Normalized tree**: `dict` / `list` / `str` / `int` / `float` / `bool` / `None`, plus
  `datetime.date` / `datetime.time` / `datetime.datetime` as a deliberate extension (YAML and
  TOML both have native timestamp types; forcing them to strings at parse time would silently
  destroy information the source format actually carries).
* **List order matters.** `[1, 2, 3]` vs `[3, 2, 1]` is reported as a real difference at each
  differing index -- cfgdiff does not attempt reorder-aware (LCS-style) list diffing. This is
  a deliberate, tested policy: most config lists (ports, allowed IPs in priority order, etc.)
  are order-sensitive, and there's no general way to tell an ordered list from an unordered set
  just by looking at the tree.
* **Type changed vs. value changed**: at a given path, if both sides have a value and
  `type(a) is not type(b)` (strict -- `bool` is never conflated with `int`, so `true` vs `1`
  is a type change, not "equal"), it's reported as `type_changed`; if the types match but the
  values differ, it's `value_changed`.
* **Cross-format string coercion policy**: INI and `.env` have no native type system --
  every value is a string. Diffing `PORT=8080` (.env) against `port: 8080` (YAML) naively
  would report `type_changed` on *every single key*, which is just noise about a format
  limitation, not a real difference. So: when exactly one side of a `diff` comes from a
  string-only format (INI/`.env`) and the other doesn't, cfgdiff coerces the string-only
  side's leaves (try bool, then int, then float, else leave as string) before comparing.
  When *both* sides are string-only, or *neither* is, no coercion happens. See the
  `diff.py` module docstring for the exact algorithm; `tests/test_cross_format.py` and
  `tests/test_diff.py::TestCoercion` exercise it directly.
* **`.env`/`.ini` values are always strings.** This is a deliberate policy, not a bug --
  neither format has a quoting convention that distinguishes `5` the integer from `"5"` the
  string, so cfgdiff doesn't pretend otherwise.
* **Convert warnings (non-fatal, to stderr)**: YAML anchors/aliases (detected as
  shared/duplicate object identity in the parsed tree) get duplicated independently in the
  output; non-string YAML dict keys get stringified for JSON/TOML output (and a further
  warning if that stringification collides with an existing key); TOML/YAML datetime values
  get stringified to ISO-8601 for JSON output (JSON has no datetime type).
* **Convert hard errors (fatal, exit 2)**: a `null`/`None` value converted to TOML (TOML has
  no null type at all -- there's no lossy-but-valid representation, so cfgdiff refuses rather
  than silently dropping the key); a non-mapping document root converted to TOML (TOML
  documents are always a table at the root).

## Supported formats

| Format | Extension(s)             | Notes |
|--------|---------------------------|-------|
| JSON   | `.json`                   | stdlib `json` |
| YAML   | `.yaml`, `.yml`            | PyYAML `safe_load`/`safe_dump` |
| TOML   | `.toml`                   | `tomllib` (Python >=3.11) / `tomli` (3.10) for reading, `tomli-w` for writing |
| INI    | `.ini`, `.cfg`, `.conf`    | stdlib `configparser`; requires at least one `[section]` |
| .env   | `.env`, `.env.*`           | hand-rolled parser (no `python-dotenv` dependency) |

Convert targets are `yaml`, `json`, `toml` only (per spec) -- INI and `.env` are read-only
in cfgdiff, since re-emitting an arbitrarily nested tree as flat `KEY=VALUE` pairs has no
general, lossless answer.

## `--help` output

<details>
<summary><code>cfgdiff --help</code></summary>

```
usage: cfgdiff [-h] [--version] {diff,convert,validate} ...

Semantic config diff/convert across JSON, YAML, TOML, INI, and .env files.
Parses each into a normalized tree and compares/re-emits by meaning, not text.

positional arguments:
  {diff,convert,validate}
    diff                Show a semantic diff between two config files (can be
                        different formats)
    convert             Convert a config file to another format
    validate            Parse-check a config file

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

</details>

<details>
<summary><code>cfgdiff diff --help</code></summary>

```
usage: cfgdiff diff [-h] [--output {text,json}] [--ignore DOTTED.PATH]
                    [--no-color] [--format-a {json,yaml,toml,ini,env}]
                    [--format-b {json,yaml,toml,ini,env}]
                    A B

Compare two config files semantically -- key order, formatting, and comments
never produce a diff; only actual structural/value differences do.

positional arguments:
  A                     first file
  B                     second file

options:
  -h, --help            show this help message and exit
  --output {text,json}  output format (default: text)
  --ignore DOTTED.PATH  ignore differences at this dotted path and its
                        children; repeatable
  --no-color            disable ANSI color in text output
  --format-a {json,yaml,toml,ini,env}
                        override format detection for A
  --format-b {json,yaml,toml,ini,env}
                        override format detection for B
```

</details>

<details>
<summary><code>cfgdiff convert --help</code></summary>

```
usage: cfgdiff convert [-h] --to {yaml,json,toml} [-o OUTPUT]
                       [--from {json,yaml,toml,ini,env}]
                       A

Parse A into a normalized tree and re-emit it in a different format.

positional arguments:
  A                     source file

options:
  -h, --help            show this help message and exit
  --to {yaml,json,toml}
                        target format
  -o OUTPUT, --output OUTPUT
                        write to this file instead of stdout
  --from {json,yaml,toml,ini,env}
                        override format detection for A
```

</details>

<details>
<summary><code>cfgdiff validate --help</code></summary>

```
usage: cfgdiff validate [-h] [--format {json,yaml,toml,ini,env}] FILE

Parse FILE and report OK, or a clear error with file:line:col location.

positional arguments:
  FILE

options:
  -h, --help            show this help message and exit
  --format {json,yaml,toml,ini,env}
                        override format detection
```

</details>

## Development

```bash
pip install -e '.[dev]'
ruff check .
pytest
```

## Status

`cfgdiff` is `0.1.1`. It is not yet published to PyPI -- install from GitHub (see above)
until it is. See `CHANGELOG.md` for release history.

## License

MIT -- see `LICENSE`.
