"""Hand-rolled .env parser (deliberately no ``python-dotenv`` dependency).

Supported grammar, one assignment per line:

* ``KEY=VALUE`` and ``export KEY=VALUE``
* Double-quoted values (``KEY="a b"``) with backslash escapes
  (``\\n``, ``\\t``, ``\\"``, ``\\\\``, ...) unescaped via Python's
  ``unicode_escape`` codec.
* Single-quoted values (``KEY='a b'``) taken *literally* -- no escape
  processing, matching shell single-quote semantics.
* Unquoted values, trimmed of surrounding whitespace, with a trailing
  ``#`` comment stripped when it is preceded by whitespace (``KEY=1 # note``
  -> ``"1"``; ``KEY=a#b`` is left as ``"a#b"``, since an unspaced ``#`` is
  common in unquoted values like URLs or colors and dotenv tooling
  generally does not treat it as a comment starter there).
* Full-line comments (optional leading whitespace then ``#``) and blank
  lines are ignored.

Policy: every value is a ``str``, always -- .env is inherently a stringly
typed format (there's no quoting convention that distinguishes ``5`` the
integer from ``"5"`` the string). This is documented, deliberate, and
consistent with the INI parser; cross-format comparisons handle it via
diff.py's coercion policy, not by guessing types here.
"""

from __future__ import annotations

import re

from ..errors import ParseError

_LINE_RE = re.compile(
    r"""^[ \t]*
    (?:export[ \t]+)?
    (?P<key>[A-Za-z_][A-Za-z0-9_]*)
    [ \t]*=[ \t]*
    (?P<value>.*)
    $""",
    re.VERBOSE,
)

_COMMENT_RE = re.compile(r"(?:^|[ \t])#.*$")


def load(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        raise ParseError(path, f"cannot read file: {e}") from e

    result: dict[str, str] = {}
    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n").rstrip("\r")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _LINE_RE.match(line)
        if not m:
            raise ParseError(path, f"invalid assignment: {line!r}", line=lineno)
        key = m.group("key")
        try:
            value = _parse_value(m.group("value"))
        except ValueError as e:
            raise ParseError(path, str(e), line=lineno) from e
        result[key] = value
    return result


def _parse_value(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0] == '"':
        return _parse_quoted(raw, '"', unescape=True)
    if raw[0] == "'":
        return _parse_quoted(raw, "'", unescape=False)
    return _strip_inline_comment(raw).strip()


def _parse_quoted(raw: str, quote: str, unescape: bool) -> str:
    end = raw.find(quote, 1)
    if end == -1:
        raise ValueError(f"unterminated {quote!r}-quoted value: {raw!r}")
    inner = raw[1:end]
    if unescape:
        inner = inner.encode("utf-8", "surrogateescape").decode("unicode_escape")
    return inner


def _strip_inline_comment(value: str) -> str:
    m = _COMMENT_RE.search(value)
    if m:
        return value[: m.start()]
    return value
