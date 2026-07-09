"""Format detection and dispatch for cfgdiff's five supported config formats."""

from __future__ import annotations

import os

from . import env_parser, ini_parser, json_parser, toml_parser, yaml_parser

#: All formats cfgdiff can read.
SUPPORTED_FORMATS = ("json", "yaml", "toml", "ini", "env")

#: Formats that are inherently string-only (every leaf value is a str).
#: Used by diff.py's cross-format coercion policy -- see diff.py module docstring.
STRING_ONLY_FORMATS = frozenset({"ini", "env"})

_EXTENSION_MAP = {
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "ini",
    ".env": "env",
}

_LOADERS = {
    "json": json_parser.load,
    "yaml": yaml_parser.load,
    "toml": toml_parser.load,
    "ini": ini_parser.load,
    "env": env_parser.load,
}


def detect_format(path: str) -> str:
    """Infer a format name from a file's name/extension.

    ``.env`` and any ``*.env`` filename (e.g. ``.env.production``) are
    detected as the ``env`` format regardless of extension, since dotenv
    files conventionally have no extension of their own.
    """
    base = os.path.basename(path)
    if base == ".env" or base.endswith(".env") or base.startswith(".env."):
        return "env"
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in _EXTENSION_MAP:
        return _EXTENSION_MAP[ext]
    raise ValueError(
        f"cannot infer a config format from {path!r} (unrecognized extension {ext!r}); "
        "pass an explicit --format/--format-a/--format-b/--from override"
    )


def load_file(path: str, fmt: str | None = None) -> tuple[str, object]:
    """Parse *path* and return ``(format_name, normalized_tree)``.

    If *fmt* is given it is used as-is (skipping extension detection);
    otherwise the format is inferred via :func:`detect_format`.
    """
    resolved = fmt or detect_format(path)
    if resolved not in _LOADERS:
        raise ValueError(
            f"unknown format {resolved!r}; supported formats are {', '.join(SUPPORTED_FORMATS)}"
        )
    if not os.path.exists(path):
        raise ValueError(f"file not found: {path}")
    return resolved, _LOADERS[resolved](path)
