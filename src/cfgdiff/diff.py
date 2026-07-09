"""Semantic tree differ.

Two normalized trees are compared by walking them together and reporting
leaf-level differences addressed by a dotted/bracketed path, e.g.
``server.host``, ``server.ports[2]``, ``db.credentials.user``.

## Type changed vs. value changed

At any given path, if both sides have a value:

* If ``type(a) is not type(b)`` (a *strict* check -- ``bool`` is not
  conflated with ``int`` even though ``bool`` subclasses it in Python, so
  ``true`` vs ``1`` is correctly reported as a type change, not treated as
  equal), the entry is ``"type_changed"``.
* Otherwise, if ``a != b``, the entry is ``"value_changed"``.
* Otherwise there is no entry -- they're equal.

## List order policy

Lists are compared **index-wise**: element ``i`` of A is compared against
element ``i`` of B. Two lists containing the same elements in a different
order are reported as differences at each differing index -- cfgdiff does
not attempt reorder-aware/LCS-style list diffing. This is a deliberate,
documented, tested policy choice (config lists like ``server.ports`` are
usually order-sensitive; treating reorders as no-ops would hide real
changes for ordered data, and there's no reliable way to tell ordered lists
from unordered sets from the tree alone). If the lists differ in length,
the extra indices on the longer side show up as ``added``/``removed``.

## Cross-format string coercion policy

INI and ``.env`` (``diff.STRING_ONLY_FORMATS`` via
``cfgdiff.parsers.STRING_ONLY_FORMATS``) have no native type system --every
leaf is a ``str``. Compared naively against a JSON/YAML/TOML tree, ``"5"``
vs ``5`` would show up as a type change on *every single key*, which is
noise: the string-only format is not "wrong", it structurally cannot
represent an int.

The policy, applied by the CLI layer (see ``cli.py::_cmd_diff``) before
calling :func:`diff_trees`:

* If exactly one side's source format is string-only and the other is not,
  the string-only side's leaves are coerced with :func:`coerce_tree` before
  diffing: each string leaf is tried, in order, as a case-insensitive
  ``bool`` (``"true"``/``"false"``), then ``int``, then ``float``; the
  first that round-trips is used, otherwise the original string is kept.
  After coercion, the normal type/value rules above apply -- so a
  genuinely-typed difference (``"5"`` coerced to ``5`` vs. YAML's
  ``5.0``) still correctly reports as ``type_changed`` (int vs float).
* If *both* sides are string-only (INI vs ``.env``), or *neither* is
  (JSON/YAML/TOML against each other), no coercion happens -- values are
  compared as-is.

This keeps native-vs-native diffs strict (a real type mismatch always
shows), while making string-only-vs-native diffs useful instead of
uniformly noisy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_MISSING = object()


@dataclass
class DiffEntry:
    path: str
    kind: str  # "added" | "removed" | "value_changed" | "type_changed"
    old: Any = None
    new: Any = None


def diff_trees(
    a: Any, b: Any, ignore_prefixes: tuple[str, ...] | list[str] = ()
) -> list[DiffEntry]:
    """Diff two normalized trees, returning a list of :class:`DiffEntry`.

    ``ignore_prefixes`` is a list of dotted paths; any entry whose path is
    equal to, or a dotted/bracketed descendant of, one of these prefixes is
    dropped from the result.
    """
    entries: list[DiffEntry] = []
    _diff(a, b, "", entries)
    if ignore_prefixes:
        entries = [e for e in entries if not _is_ignored(e.path, ignore_prefixes)]
    return entries


def _is_ignored(path: str, prefixes) -> bool:
    for prefix in prefixes:
        if path == prefix or path.startswith(prefix + ".") or path.startswith(prefix + "["):
            return True
    return False


def _diff(a: Any, b: Any, path: str, entries: list[DiffEntry]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b), key=str):
            child = f"{path}.{key}" if path else str(key)
            if key not in a:
                entries.append(DiffEntry(child, "added", None, b[key]))
            elif key not in b:
                entries.append(DiffEntry(child, "removed", a[key], None))
            else:
                _diff(a[key], b[key], child, entries)
        return

    if isinstance(a, list) and isinstance(b, list):
        for i in range(max(len(a), len(b))):
            child = f"{path}[{i}]"
            if i >= len(a):
                entries.append(DiffEntry(child, "added", None, b[i]))
            elif i >= len(b):
                entries.append(DiffEntry(child, "removed", a[i], None))
            else:
                _diff(a[i], b[i], child, entries)
        return

    if type(a) is not type(b):
        entries.append(DiffEntry(path, "type_changed", a, b))
    elif a != b:
        entries.append(DiffEntry(path, "value_changed", a, b))


_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+[eE][+-]?\d+)$")


def coerce_scalar(value: Any) -> Any:
    """Best-effort coerce a single string leaf to bool/int/float.

    Non-strings pass through unchanged. See the module docstring's
    "Cross-format string coercion policy" section.
    """
    if not isinstance(value, str):
        return value
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_RE.match(value):
        return int(value)
    if _FLOAT_RE.match(value):
        return float(value)
    return value


def coerce_tree(tree: Any) -> Any:
    """Recursively apply :func:`coerce_scalar` to every leaf of a tree."""
    if isinstance(tree, dict):
        return {k: coerce_tree(v) for k, v in tree.items()}
    if isinstance(tree, list):
        return [coerce_tree(v) for v in tree]
    return coerce_scalar(tree)
