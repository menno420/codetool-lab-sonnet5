"""argparse-based CLI: ``cfgdiff diff|convert|validate``."""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from typing import Any

from . import __version__
from .convert import TO_FUNCS
from .diff import DiffEntry, coerce_tree, diff_trees
from .errors import CfgDiffError
from .parsers import STRING_ONLY_FORMATS, SUPPORTED_FORMATS, load_file

_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def _json_default(o: Any) -> Any:
    if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
        return o.isoformat()
    raise TypeError(f"object of type {type(o).__name__} is not JSON serializable")


def _fmt_val(v: Any) -> str:
    try:
        return json.dumps(v, default=_json_default)
    except TypeError:
        return repr(v)


def _use_color(no_color: bool) -> bool:
    return (not no_color) and sys.stdout.isatty()


def _format_entry(e: DiffEntry, color: bool) -> str:
    def c(code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if color else text

    if e.kind == "added":
        return c(_GREEN, f"+ {e.path}: {_fmt_val(e.new)}")
    if e.kind == "removed":
        return c(_RED, f"- {e.path}: {_fmt_val(e.old)}")
    if e.kind == "value_changed":
        return c(_YELLOW, f"~ {e.path}: {_fmt_val(e.old)} -> {_fmt_val(e.new)}")
    if e.kind == "type_changed":
        return c(
            _YELLOW,
            f"~ {e.path}: {_fmt_val(e.old)} ({type(e.old).__name__}) -> "
            f"{_fmt_val(e.new)} ({type(e.new).__name__}) [type changed]",
        )
    return f"? {e.path}"  # pragma: no cover - defensive, all kinds handled above


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cfgdiff",
        description=(
            "Semantic config diff/convert across JSON, YAML, TOML, INI, and .env files. "
            "Parses each into a normalized tree and compares/re-emits by meaning, not text."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    diff_p = sub.add_parser(
        "diff",
        help="Show a semantic diff between two config files (can be different formats)",
        description="Compare two config files semantically -- key order, formatting, and "
        "comments never produce a diff; only actual structural/value differences do.",
    )
    diff_p.add_argument("a", metavar="A", help="first file")
    diff_p.add_argument("b", metavar="B", help="second file")
    diff_p.add_argument(
        "--output", choices=["text", "json"], default="text", help="output format (default: text)"
    )
    diff_p.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="DOTTED.PATH",
        help="ignore differences at this dotted path and its children; repeatable",
    )
    diff_p.add_argument("--no-color", action="store_true", help="disable ANSI color in text output")
    diff_p.add_argument(
        "--format-a", choices=SUPPORTED_FORMATS, help="override format detection for A"
    )
    diff_p.add_argument(
        "--format-b", choices=SUPPORTED_FORMATS, help="override format detection for B"
    )

    conv_p = sub.add_parser(
        "convert",
        help="Convert a config file to another format",
        description="Parse A into a normalized tree and re-emit it in a different format.",
    )
    conv_p.add_argument("a", metavar="A", help="source file")
    conv_p.add_argument(
        "--to", required=True, choices=["yaml", "json", "toml"], help="target format"
    )
    conv_p.add_argument(
        "-o", "--output", metavar="OUTPUT", help="write to this file instead of stdout"
    )
    conv_p.add_argument(
        "--from",
        dest="from_format",
        choices=SUPPORTED_FORMATS,
        help="override format detection for A",
    )

    val_p = sub.add_parser(
        "validate",
        help="Parse-check a config file",
        description="Parse FILE and report OK, or a clear error with file:line:col location.",
    )
    val_p.add_argument("file", metavar="FILE")
    val_p.add_argument("--format", choices=SUPPORTED_FORMATS, help="override format detection")

    return parser


def _cmd_diff(args: argparse.Namespace) -> int:
    fmt_a, tree_a = load_file(args.a, args.format_a)
    fmt_b, tree_b = load_file(args.b, args.format_b)

    a_stringy = fmt_a in STRING_ONLY_FORMATS
    b_stringy = fmt_b in STRING_ONLY_FORMATS
    if a_stringy and not b_stringy:
        tree_a = coerce_tree(tree_a)
    elif b_stringy and not a_stringy:
        tree_b = coerce_tree(tree_b)

    entries = diff_trees(tree_a, tree_b, ignore_prefixes=args.ignore)

    if args.output == "json":
        payload = [{"path": e.path, "kind": e.kind, "old": e.old, "new": e.new} for e in entries]
        print(json.dumps(payload, indent=2, default=_json_default))
    else:
        color = _use_color(args.no_color)
        if not entries:
            msg = "no differences"
            print(f"{_GREEN}{msg}{_RESET}" if color else msg)
        else:
            for e in entries:
                print(_format_entry(e, color))

    return 0 if not entries else 1


def _cmd_convert(args: argparse.Namespace) -> int:
    _fmt, tree = load_file(args.a, args.from_format)
    warnings: list[str] = []
    text = TO_FUNCS[args.to](tree, warnings.append)
    for w in warnings:
        print(f"cfgdiff: warning: {w}", file=sys.stderr)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    fmt, _tree = load_file(args.file, args.format)
    print(f"OK: {args.file} ({fmt})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "diff":
            return _cmd_diff(args)
        if args.command == "convert":
            return _cmd_convert(args)
        if args.command == "validate":
            return _cmd_validate(args)
        parser.error(f"unknown command: {args.command}")  # pragma: no cover
        return 2
    except CfgDiffError as e:
        print(f"cfgdiff: error: {e}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print(f"cfgdiff: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
