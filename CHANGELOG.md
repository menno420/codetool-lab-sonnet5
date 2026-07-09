# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/menno420/codetool-lab-sonnet5/releases/tag/v0.1.0
