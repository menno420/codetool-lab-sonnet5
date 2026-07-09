"""YAML parser: wraps PyYAML's ``safe_load``.

Notes on normalization:

* An empty YAML document parses to ``None`` (this mirrors YAML's own
  semantics -- an empty document *is* the null scalar -- unlike TOML/INI/env
  where "empty file" naturally means "empty mapping").
* PyYAML's ``SafeLoader`` resolves unquoted ISO-8601-looking scalars to
  ``datetime.date``/``datetime.datetime`` objects (its ``!!timestamp``
  resolver). cfgdiff's normalized tree deliberately allows these datetime
  types through as leaves (in addition to the base
  dict/list/str/int/float/bool/None set) specifically so that YAML/TOML
  datetimes compare and convert meaningfully -- see convert.py for how they
  are handled when the target format can't represent them (JSON).
* YAML anchors/aliases are resolved transparently by ``safe_load``: aliased
  nodes become the *same* Python object (shared by identity). cfgdiff
  detects this via identity-based structural sharing in convert.py and
  warns rather than silently duplicating.
"""

from __future__ import annotations

import yaml

from ..errors import ParseError


def load(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise ParseError(path, f"cannot read file: {e}") from e
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        line = col = None
        mark = getattr(e, "problem_mark", None)
        if mark is not None:
            line = mark.line + 1
            col = mark.column + 1
        msg = getattr(e, "problem", None) or str(e)
        context = getattr(e, "context", None)
        if context:
            msg = f"{context}; {msg}"
        raise ParseError(path, msg, line=line, col=col) from e
