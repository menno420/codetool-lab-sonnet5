# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-09

### Added

- Tag-triggered release automation (`.github/workflows/release.yml`): pushing a `v*` tag
  builds sdist+wheel, runs the test suite as a gate, creates a GitHub release whose body is
  the matching CHANGELOG section (artifacts attached), then publishes to PyPI via trusted
  publishing (`pypi` environment; fails cleanly until the trusted publisher is registered).
- Differential .env test corpus (`tests/test_dotenv_differential.py`) comparing our parser
  against python-dotenv's `dotenv_values` across quoting, escaping, comment, whitespace,
  and CRLF edge cases; deliberate divergences and known gaps are tracked as strict xfails.
- `python-dotenv` added to the `dev` extra (test-only; runtime dependencies unchanged).

### Fixed

Three `.env` parser bugs found by the differential corpus (each contradicted the parser's
own documented behaviour):

- Escaped double quotes inside double-quoted values (`KEY="a\"b"`) no longer raise
  `ParseError`: the closing-quote scan is now escape-aware, so the value parses to `a"b`.
- Non-ASCII text inside double-quoted values (`KEY="héllo"`) is no longer mojibaked
  (`hÃ©llo`): backslash escapes are decoded per-sequence instead of round-tripping the
  whole value through `unicode_escape`, so `\n`/`\t`/`\uXXXX` etc. still work while
  literal Unicode passes through untouched. Unknown escapes (`\q`) are kept literally.
- A value-initial `#` in unquoted values (`COLOR=#ff0000`) is no longer swallowed as a
  comment: `#` starts an inline comment only when preceded by whitespace (including the
  whitespace right after `=`, so `KEY= # note` is still `""`).

## [0.1.0] - 2026-07-09

### Added

- Initial release of `cfgdiff`, a semantic config diff/convert CLI.
- Parsers for JSON, YAML, TOML, INI, and `.env`, each producing a normalized tree.
- `cfgdiff diff A B` -- semantic, cross-format-capable diff with `--output text|json`,
  repeatable `--ignore DOTTED.PATH`, `--no-color`, and `--format-a`/`--format-b` overrides.
  Exit codes: `0` identical, `1` differences found, `2` error.
- `cfgdiff convert A --to {yaml,json,toml}` -- re-emit a parsed config in another format,
  with non-fatal stderr warnings for lossy constructs (YAML anchors/aliases, non-string
  keys, TOML/YAML datetimes going to JSON) and hard errors for unrepresentable ones
  (`null` to TOML, non-mapping root to TOML).
- `cfgdiff validate FILE` -- parse-check with a clear `file:line:col` error on failure.
- Documented, tested policies for list-order-matters diffing and cross-format string
  coercion between string-only formats (INI/.env) and natively-typed ones (JSON/YAML/TOML).
- Full pytest suite (114 tests) and `ruff` lint config.
- GitHub Actions CI across Python 3.10, 3.11, 3.12.

[0.1.1]: https://github.com/menno420/codetool-lab-sonnet5/releases/tag/v0.1.1
[0.1.0]: https://github.com/menno420/codetool-lab-sonnet5/releases/tag/v0.1.0
