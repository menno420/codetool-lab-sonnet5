"""INI parser: wraps stdlib ``configparser``.

Normalization policy:

* The tree is always ``{section_name: {key: value}}`` -- a two-level dict.
  Bare ``key = value`` lines outside of any ``[section]`` header are a parse
  error, matching ``configparser``'s own default behavior
  (``MissingSectionHeaderError``); INI without at least one section header
  is not something cfgdiff tries to guess at.
* Key case is preserved as-written (``optionxform = str``); vanilla
  ``configparser`` lowercases keys by default, which would silently corrupt
  case-sensitive keys during diff/convert.
* Every value is a ``str`` -- INI has no native type system. This is a
  deliberate policy (see diff.py's cross-format coercion policy), not a
  limitation to work around.
* ``[DEFAULT]`` section values are, per ``configparser`` semantics, merged
  as fallbacks into every other section's item view. cfgdiff surfaces this
  standard INI behavior as-is rather than hiding it: if a file has a
  ``[DEFAULT]`` section, its keys appear both under ``"DEFAULT"`` in the
  tree *and* inherited into every other section that doesn't override them.
"""

from __future__ import annotations

import configparser

from ..errors import ParseError


def load(path: str):
    parser = configparser.ConfigParser()
    parser.optionxform = str  # type: ignore[method-assign]  # preserve key case
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise ParseError(path, f"cannot read file: {e}") from e
    try:
        parser.read_string(text, source=path)
    except configparser.Error as e:
        line = getattr(e, "lineno", None)
        message = str(e).splitlines()[0]
        raise ParseError(path, message, line=line) from e

    tree: dict[str, dict[str, str]] = {}
    if parser.defaults():
        tree["DEFAULT"] = dict(parser.defaults())
    for section in parser.sections():
        tree[section] = dict(parser.items(section))
    return tree
