"""JSON parser: thin wrapper around the stdlib ``json`` module."""

from __future__ import annotations

import json

from ..errors import ParseError


def load(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise ParseError(path, f"cannot read file: {e}") from e
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ParseError(path, e.msg, line=e.lineno, col=e.colno) from e
