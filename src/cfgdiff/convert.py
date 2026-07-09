"""Re-emit a normalized tree in a target format: yaml, json, or toml.

Each ``to_*`` function takes a ``warn`` callback (``str -> None``) that is
called zero or more times with a human-readable, non-fatal warning about a
lossy or approximated conversion. The CLI prints these to stderr; they never
abort the conversion. Genuinely *unrepresentable* constructs (see below)
raise :class:`cfgdiff.errors.ConvertError` instead, since silently dropping
data or guessing would be worse than failing loudly.

## What's warned on (specific to this implementation)

* **Shared/aliased structure** -- if the same list/dict object appears at
  more than one path in the source tree (Python object identity), this is
  how a YAML anchor/alias (``&x`` / ``*x``) surfaces once ``yaml.safe_load``
  has resolved it. The target format has no equivalent concept (cfgdiff
  never re-emits YAML anchors even when the target *is* yaml), so the
  content is duplicated independently in the output -- warned once per
  duplicate path found.
* **Non-string dict keys stringified** -- only reachable via a YAML source
  (e.g. ``1: foo`` parses to an int key); JSON and TOML both require string
  keys. Warned, and if stringifying two different keys collides (e.g. an
  int key ``1`` and a string key ``"1"`` both present), that's warned too
  (the later key wins, matching plain dict-literal semantics).
* **Datetime values converted to ISO-8601 strings for JSON** -- TOML/YAML
  datetimes (``datetime.date``/``time``/``datetime``) have no JSON
  equivalent, so JSON output stringifies them via ``.isoformat()``. YAML and
  TOML targets keep them as native datetime values (both PyYAML's dumper
  and ``tomli-w`` support them directly), so no warning is emitted for
  those targets.

## What's a hard error, not a warning

* **``None``/``null`` values going to TOML** -- TOML has no null type at
  all, not even an approximate one; there's no lossy-but-valid
  representation, so this raises :class:`cfgdiff.errors.ConvertError`
  rather than silently dropping the key.
* **A non-mapping document root going to TOML** -- TOML documents are
  always a table at the root; a source tree whose root is a list or scalar
  (only possible from JSON/YAML) cannot be a TOML document at all.
"""

from __future__ import annotations

import datetime
import json as _json
from collections.abc import Callable
from typing import Any

import tomli_w
import yaml

from .errors import ConvertError

WarnFn = Callable[[str], None]


def _noop_warn(_msg: str) -> None:
    return None


def detect_shared_refs(tree: Any):
    """Yield ``(first_path, second_path)`` for every container object that
    is reachable at more than one path in *tree* (by Python object
    identity) -- the signature of a resolved YAML anchor/alias."""
    seen: dict[int, str] = {}
    for path, obj in _walk_containers(tree, "$"):
        key = id(obj)
        if key in seen:
            yield seen[key], path
        else:
            seen[key] = path


def _walk_containers(node: Any, path: str):
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from _walk_containers(v, f"{path}.{k}")
    elif isinstance(node, list):
        yield path, node
        for i, v in enumerate(node):
            yield from _walk_containers(v, f"{path}[{i}]")


def _check_shared_refs(tree: Any, warn: WarnFn) -> None:
    for first_path, second_path in detect_shared_refs(tree):
        warn(
            f"structure shared between {first_path} and {second_path} in the source "
            "(e.g. a YAML anchor/alias) will be duplicated independently in the output"
        )


def _stringify_keys(node: Any, target: str, warn: WarnFn, path: str) -> Any:
    if isinstance(node, dict):
        new: dict[str, Any] = {}
        origin_of: dict[str, Any] = {}
        for k, v in node.items():
            if isinstance(k, str):
                sk = k
            else:
                sk = str(k)
                warn(f"{path}: non-string key {k!r} stringified to {sk!r} for {target} output")
            if sk in origin_of:
                warn(
                    f"{path}: key collision after stringification -- {origin_of[sk]!r} and "
                    f"{k!r} both become {sk!r}; the latter overwrites the former"
                )
            origin_of[sk] = k
            new[sk] = _stringify_keys(v, target, warn, f"{path}.{sk}")
        return new
    if isinstance(node, list):
        return [_stringify_keys(v, target, warn, f"{path}[{i}]") for i, v in enumerate(node)]
    return node


def _stringify_datetimes(node: Any, warn: WarnFn, path: str) -> Any:
    if isinstance(node, dict):
        return {k: _stringify_datetimes(v, warn, f"{path}.{k}") for k, v in node.items()}
    if isinstance(node, list):
        return [_stringify_datetimes(v, warn, f"{path}[{i}]") for i, v in enumerate(node)]
    if isinstance(node, (datetime.datetime, datetime.date, datetime.time)):
        warn(
            f"{path}: datetime value {node!r} converted to an ISO-8601 string for JSON output "
            "(JSON has no native datetime type)"
        )
        return node.isoformat()
    return node


def _reject_none(node: Any, path: str) -> None:
    if node is None:
        raise ConvertError(f"{path}: TOML has no null/None type; cannot represent this value")
    if isinstance(node, dict):
        for k, v in node.items():
            _reject_none(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _reject_none(v, f"{path}[{i}]")


def to_json(tree: Any, warn: WarnFn = _noop_warn) -> str:
    _check_shared_refs(tree, warn)
    prepared = _stringify_keys(tree, "json", warn, "$")
    prepared = _stringify_datetimes(prepared, warn, "$")
    return _json.dumps(prepared, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def to_yaml(tree: Any, warn: WarnFn = _noop_warn) -> str:
    _check_shared_refs(tree, warn)
    return yaml.safe_dump(tree, sort_keys=False, allow_unicode=True)


def to_toml(tree: Any, warn: WarnFn = _noop_warn) -> str:
    if not isinstance(tree, dict):
        raise ConvertError(
            "TOML documents must have a table (mapping) at the root; "
            f"source root is a {type(tree).__name__}"
        )
    _check_shared_refs(tree, warn)
    prepared = _stringify_keys(tree, "toml", warn, "$")
    _reject_none(prepared, "$")
    try:
        return tomli_w.dumps(prepared)
    except (TypeError, ValueError) as e:
        raise ConvertError(f"cannot represent value in TOML: {e}") from e


TO_FUNCS: dict[str, Callable[[Any, WarnFn], str]] = {
    "json": to_json,
    "yaml": to_yaml,
    "toml": to_toml,
}
