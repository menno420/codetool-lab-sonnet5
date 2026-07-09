"""Error types raised by cfgdiff."""

from __future__ import annotations


class CfgDiffError(Exception):
    """Base class for all cfgdiff errors."""


class ParseError(CfgDiffError):
    """Raised when a config file cannot be parsed.

    Carries the file path and, where the underlying library provides it, a
    line/column location, so the CLI can print a ``path:line:col: message``
    style error.
    """

    def __init__(
        self,
        path: str,
        message: str,
        line: int | None = None,
        col: int | None = None,
    ) -> None:
        self.path = path
        self.message = message
        self.line = line
        self.col = col
        location = ""
        if line is not None:
            location = f":{line}"
            if col is not None:
                location += f":{col}"
        super().__init__(f"{path}{location}: {message}")


class ConvertError(CfgDiffError):
    """Raised when a normalized tree cannot be represented in a target format."""
