"""TOML parser.

Uses the stdlib ``tomllib`` on Python >= 3.11, and falls back to the
``tomli`` backport (same API) on Python 3.10. This project targets Python
3.10+, so the branch is required; both expose an identical
``loads``/``TOMLDecodeError`` surface, so the rest of cfgdiff never needs to
know which one is in use.

TOML's native ``datetime``/``date``/``time`` values are passed through
unchanged as normalized-tree leaves (see yaml_parser.py's docstring for why
that's an intentional, documented extension of the base leaf type set).
"""

from __future__ import annotations

import re
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ..errors import ParseError

_LOC_RE = re.compile(r"line (\d+), column (\d+)")


def load(path: str):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        raise ParseError(path, f"cannot read file: {e}") from e
    try:
        return tomllib.loads(data.decode("utf-8"))
    except tomllib.TOMLDecodeError as e:
        line = col = None
        m = _LOC_RE.search(str(e))
        if m:
            line, col = int(m.group(1)), int(m.group(2))
        raise ParseError(path, str(e), line=line, col=col) from e
    except UnicodeDecodeError as e:
        raise ParseError(path, f"not valid utf-8: {e}") from e
