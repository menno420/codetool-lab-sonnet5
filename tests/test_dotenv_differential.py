"""Differential .env tests: our hand-rolled parser vs python-dotenv's ``dotenv_values``.

Targets the retro A3 confidence gap: our .env parser was written from scratch with no
reference-implementation cross-check. Every case here feeds the same file to both
parsers and asserts identical key/value readings.

Where the two legitimately diverge, the case is kept (never deleted) and marked
``xfail(strict=True)`` with the reason:

* "documented divergence" -- our env_parser docstring deliberately specifies different
  behaviour (shell-literal single quotes; full ``unicode_escape`` repertoire in double
  quotes; ``#`` preceded by whitespace always starts a comment in unquoted values).
* "known gap" -- behaviour that contradicts our own docstring, surfaced by this corpus
  and tracked as follow-up work (escape-unaware closing-quote scan; non-ASCII mojibake
  in double-quoted values; value-initial ``#`` swallowed in unquoted values).

``strict=True`` means fixing a gap without updating its marker fails the suite, so the
corpus stays honest in both directions.
"""

from __future__ import annotations

import pytest
from dotenv import dotenv_values

from cfgdiff.parsers import env_parser


def case(id_: str, content: str) -> object:
    return pytest.param(content, id=id_)


def xfail_case(id_: str, content: str, reason: str) -> object:
    return pytest.param(
        content, id=id_, marks=pytest.mark.xfail(strict=True, reason=reason)
    )


DOC_SINGLE_QUOTE = (
    "documented divergence: our single-quoted values are fully literal (shell "
    "semantics, per env_parser docstring); python-dotenv decodes \\\\ and \\' inside them"
)

CORPUS = [
    # --- basics ---
    case("plain", "KEY=value\n"),
    case("spaces-around-eq", "KEY = value\n"),
    case("export-prefix", "export KEY=value\n"),
    case("export-prefix-quoted", 'export KEY="v"\n'),
    case("empty-value", "KEY=\n"),
    case("value-with-eq", "KEY=a=b\n"),
    case("value-with-eq-quoted", 'KEY="a=b"\n'),
    case("underscore-digit-key", "MY_KEY_2=ok\n"),
    case("lowercase-key", "key=1\n"),
    case("duplicate-key-last-wins", "KEY=1\nKEY=2\n"),
    case("multiple-mixed", 'A=1\nexport B=\'two\'\nC="three" # c\n'),
    # --- quoting ---
    case("double-quoted", 'KEY="double quoted"\n'),
    case("single-quoted", "KEY='single quoted'\n"),
    case("dq-empty", 'KEY=""\n'),
    case("sq-empty", "KEY=''\n"),
    case("quoted-surrounding-space", 'KEY=  "v"  \n'),
    case("dq-dollar-not-expanded", 'KEY="$HOME"\n'),
    case("unquoted-dollar-not-expanded", "KEY=$HOME\n"),
    # --- escapes in double quotes ---
    case("dq-newline-escape", 'KEY="line1\\nline2"\n'),
    case("dq-tab-escape", 'KEY="a\\tb"\n'),
    case("dq-escaped-backslash", 'KEY="a\\\\b"\n'),
    xfail_case(
        "dq-escaped-quote",
        'KEY="a\\"b"\n',
        "known gap: docstring promises \\\" support but the closing-quote scan is "
        "escape-unaware, so parsing raises ParseError; python-dotenv reads 'a\"b'",
    ),
    xfail_case(
        "dq-unicode-escape",
        'KEY="\\u00e9"\n',
        "documented divergence: we decode the full unicode_escape repertoire "
        "(\\u00e9 -> 'é'); python-dotenv leaves \\uXXXX sequences literal",
    ),
    # --- escapes (not) in single quotes ---
    case("sq-no-newline-escape", "KEY='line1\\nline2'\n"),
    xfail_case("sq-backslash", "KEY='a\\\\b'\n", DOC_SINGLE_QUOTE),
    xfail_case("sq-escaped-quote", "KEY='a\\'b'\n", DOC_SINGLE_QUOTE),
    # --- comments ---
    case("full-line-comment", "# comment\nKEY=value\n"),
    case("indented-comment", "   # comment\nKEY=value\n"),
    case("unquoted-inline-comment", "KEY=value # comment\n"),
    case("unquoted-inline-comment-tab", "KEY=v\t# c\n"),
    case("unquoted-hash-no-space-kept", "KEY=a#b\n"),
    case("unquoted-url-anchor-kept", "URL=https://x.example/page#frag\n"),
    case("dq-hash-inside", 'KEY="a # not comment"\n'),
    case("sq-hash-inside", "KEY='a # not comment'\n"),
    case("dq-trailing-comment", 'KEY="value" # comment\n'),
    case("sq-trailing-comment", "KEY='value' # comment\n"),
    xfail_case(
        "value-initial-comment-spaced",
        "KEY= # comment\n",
        "documented divergence: '#' preceded by whitespace starts a comment for us "
        "even at value start (-> ''); python-dotenv reads the value '# comment'",
    ),
    xfail_case(
        "unquoted-color",
        "COLOR=#ff0000\n",
        "known gap: our docstring cites colors as motivation for keeping unspaced '#', "
        "but a value-initial '#' matches the ^-anchored comment regex and the value is "
        "swallowed to ''; python-dotenv reads '#ff0000'",
    ),
    # --- whitespace and line endings ---
    case("leading-trailing-ws", "  KEY=value  \n"),
    case("value-tabs-stripped", "KEY=\ta\t\n"),
    case("unquoted-inner-spaces-kept", "KEY=a b c\n"),
    case("blank-lines", "\n\nKEY=value\n\n"),
    case("crlf", "KEY=value\r\nOTHER=x\r\n"),
    case("crlf-quoted", 'KEY="v"\r\n'),
    case("no-trailing-newline", "KEY=value"),
    # --- non-ASCII ---
    case("nonascii-unquoted", "KEY=héllo\n"),
    case("nonascii-sq", "KEY='héllo'\n"),
    xfail_case(
        "nonascii-dq",
        'KEY="héllo"\n',
        "known gap: non-ASCII inside double quotes is mojibaked ('hÃ©llo') by the "
        "utf-8 -> unicode_escape round-trip; python-dotenv reads 'héllo'",
    ),
]


@pytest.mark.parametrize("content", CORPUS)
def test_env_parser_matches_python_dotenv(content: str, tmp_path) -> None:
    path = tmp_path / "case.env"
    # write_bytes: keep CRLF cases byte-exact, no platform newline translation
    path.write_bytes(content.encode("utf-8"))
    ours = env_parser.load(str(path))
    theirs = dict(dotenv_values(str(path)))
    assert ours == theirs
