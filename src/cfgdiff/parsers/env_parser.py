"""Hand-rolled .env parser (deliberately no ``python-dotenv`` dependency).

Supported grammar, one assignment per line:

* ``KEY=VALUE`` and ``export KEY=VALUE``
* Double-quoted values (``KEY="a b"``) with backslash escapes decoded
  sequence-by-sequence using Python's ``unicode_escape`` repertoire
  (``\\n``, ``\\t``, ``\\"``, ``\\\\``, ``\\uXXXX``, ``\\N{NAME}``, octal,
  hex, ...). The closing-quote scan is escape-aware, so ``KEY="a\\"b"``
  parses to ``a"b``. Decoding is applied per escape sequence -- never to
  the whole value -- so literal non-ASCII text (``KEY="héllo"``) passes
  through untouched. Unrecognized escapes (``\\q``) are kept literally,
  backslash included.
* Single-quoted values (``KEY='a b'``) taken *literally* -- no escape
  processing, matching shell single-quote semantics.
* Unquoted values, trimmed of surrounding whitespace. A ``#`` starts an
  inline comment only when preceded by whitespace -- including the
  whitespace right after the ``=`` (``KEY=1 # note`` -> ``"1"``;
  ``KEY= # note`` -> ``""``). A ``#`` not preceded by whitespace is part
  of the value, even as the value's first character (``KEY=a#b`` ->
  ``"a#b"``, ``COLOR=#ff0000`` -> ``"#ff0000"``,
  ``URL=https://x/p#frag`` -> unchanged), since unspaced ``#`` is common
  in unquoted values like URLs or colors and dotenv tooling generally
  does not treat it as a comment starter there.
* Full-line comments (optional leading whitespace then ``#``) and blank
  lines are ignored.

Policy: every value is a ``str``, always -- .env is inherently a stringly
typed format (there's no quoting convention that distinguishes ``5`` the
integer from ``"5"`` the string). This is documented, deliberate, and
consistent with the INI parser; cross-format comparisons handle it via
diff.py's coercion policy, not by guessing types here.
"""

from __future__ import annotations

import codecs
import re

from ..errors import ParseError

_LINE_RE = re.compile(
    r"""^[ \t]*
    (?:export[ \t]+)?
    (?P<key>[A-Za-z_][A-Za-z0-9_]*)
    [ \t]*=
    (?P<value>.*)
    $""",
    re.VERBOSE,
)

# A '#' starts an inline comment only when preceded by whitespace.
_COMMENT_RE = re.compile(r"[ \t]#.*$")

# One backslash escape sequence, longest recognized form first.
_ESCAPE_RE = re.compile(
    r"""\\(?:
        u[0-9a-fA-F]{4}     # \uXXXX
      | U[0-9a-fA-F]{8}     # \UXXXXXXXX
      | x[0-9a-fA-F]{2}     # \xXX
      | N\{[^}]*\}          # \N{UNICODE NAME}
      | [0-7]{1,3}          # octal
      | .                   # single-char escape (\n, \t, \", \\, ...)
    )""",
    re.VERBOSE | re.DOTALL,
)


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
    value = raw.strip()
    if not value:
        return ""
    if value[0] == '"':
        return _parse_quoted(value, '"', unescape=True)
    if value[0] == "'":
        return _parse_quoted(value, "'", unescape=False)
    if value[0] == "#" and raw[0] in " \t":
        # Whitespace between '=' and '#': the whole remainder is a comment.
        return ""
    return _strip_inline_comment(value).strip()


def _parse_quoted(raw: str, quote: str, unescape: bool) -> str:
    end = _find_closing_quote(raw, quote, escape_aware=unescape)
    if end == -1:
        raise ValueError(f"unterminated {quote!r}-quoted value: {raw!r}")
    inner = raw[1:end]
    if unescape:
        inner = _decode_escapes(inner)
    return inner


def _find_closing_quote(raw: str, quote: str, escape_aware: bool) -> int:
    if not escape_aware:
        return raw.find(quote, 1)
    i = 1
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == "\\":
            i += 2  # skip the escaped character (whatever it is)
            continue
        if c == quote:
            return i
        i += 1
    return -1


_SIMPLE_ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "v": "\v",
    "\\": "\\",
    "'": "'",
    '"': '"',
}


def _decode_escapes(inner: str) -> str:
    def _decode_one(m: re.Match[str]) -> str:
        seq = m.group(0)
        body = seq[1:]
        if len(body) == 1 and body not in "01234567":
            # Unknown single-char escapes are kept literally, backslash included.
            return _SIMPLE_ESCAPES.get(body, seq)
        try:
            # \uXXXX, \UXXXXXXXX, \xXX, \N{NAME}, octal
            return codecs.decode(seq, "unicode_escape")
        except ValueError:
            return seq  # undecodable escape (e.g. bad \N name): keep it literally

    return _ESCAPE_RE.sub(_decode_one, inner)


def _strip_inline_comment(value: str) -> str:
    m = _COMMENT_RE.search(value)
    if m:
        return value[: m.start()]
    return value
