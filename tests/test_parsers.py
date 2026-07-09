from __future__ import annotations

import datetime

import pytest

from cfgdiff.errors import ParseError
from cfgdiff.parsers import (
    detect_format,
    env_parser,
    ini_parser,
    json_parser,
    load_file,
    toml_parser,
    yaml_parser,
)


class TestDetectFormat:
    def test_extensions(self):
        assert detect_format("a.json") == "json"
        assert detect_format("a.yaml") == "yaml"
        assert detect_format("a.yml") == "yaml"
        assert detect_format("a.toml") == "toml"
        assert detect_format("a.ini") == "ini"
        assert detect_format("a.cfg") == "ini"
        assert detect_format(".env") == "env"
        assert detect_format(".env.production") == "env"
        assert detect_format("/path/to/.env") == "env"

    def test_unknown_extension_raises(self):
        with pytest.raises(ValueError, match="cannot infer"):
            detect_format("a.xyz")

    def test_load_file_missing(self, tmp_path):
        with pytest.raises(ValueError, match="file not found"):
            load_file(str(tmp_path / "nope.json"))


class TestJsonParser:
    def test_parses_nested(self, write):
        p = write("a.json", '{"a": {"b": [1, 2, 3], "c": null}}')
        assert json_parser.load(str(p)) == {"a": {"b": [1, 2, 3], "c": None}}

    def test_malformed_reports_line_col(self, write):
        p = write("bad.json", '{\n  "a": ,\n}')
        with pytest.raises(ParseError) as exc:
            json_parser.load(str(p))
        assert exc.value.line == 2
        assert exc.value.col is not None

    def test_missing_file(self, tmp_path):
        with pytest.raises(ParseError):
            json_parser.load(str(tmp_path / "nope.json"))


class TestYamlParser:
    def test_parses_nested(self, write):
        p = write("a.yaml", "a:\n  b:\n    - 1\n    - 2\n  c: null\n")
        assert yaml_parser.load(str(p)) == {"a": {"b": [1, 2], "c": None}}

    def test_empty_file_is_none(self, write):
        p = write("empty.yaml", "")
        assert yaml_parser.load(str(p)) is None

    def test_datetime_leaf(self, write):
        p = write("a.yaml", "created: 2024-01-01\n")
        tree = yaml_parser.load(str(p))
        assert isinstance(tree["created"], datetime.date)

    def test_malformed_reports_location(self, write):
        p = write("bad.yaml", "a: [1, 2\n")
        with pytest.raises(ParseError) as exc:
            yaml_parser.load(str(p))
        assert exc.value.line is not None

    def test_aliases_resolve_to_shared_object(self, write):
        p = write("a.yaml", "base: &b\n  x: 1\nother: *b\n")
        tree = yaml_parser.load(str(p))
        assert tree["base"] == tree["other"]
        assert tree["base"] is tree["other"]


class TestTomlParser:
    def test_parses_nested(self, write):
        p = write("a.toml", '[a]\nb = [1, 2, 3]\nname = "x"\n')
        assert toml_parser.load(str(p)) == {"a": {"b": [1, 2, 3], "name": "x"}}

    def test_datetime_leaf(self, write):
        p = write("a.toml", "created = 2024-01-01T00:00:00Z\n")
        tree = toml_parser.load(str(p))
        assert isinstance(tree["created"], datetime.datetime)

    def test_malformed_reports_location(self, write):
        p = write("bad.toml", "a = fals\n")
        with pytest.raises(ParseError) as exc:
            toml_parser.load(str(p))
        assert exc.value.line == 1
        assert exc.value.col is not None

    def test_malformed_without_location_still_raises_clear_error(self, write):
        # Not every tomllib error carries a line/col (e.g. "unclosed array at
        # end of document") -- per spec this is reported "where the
        # underlying library provides it"; when it doesn't, line/col are
        # None but the message is still present and the file path is in it.
        p = write("bad2.toml", "a = [1, 2\n")
        with pytest.raises(ParseError) as exc:
            toml_parser.load(str(p))
        assert str(p) in str(exc.value)


class TestIniParser:
    def test_parses_sections(self, write):
        p = write("a.ini", "[server]\nhost = localhost\nport = 8080\n")
        assert ini_parser.load(str(p)) == {"server": {"host": "localhost", "port": "8080"}}

    def test_values_are_always_strings(self, write):
        p = write("a.ini", "[s]\nn = 5\nb = true\n")
        tree = ini_parser.load(str(p))
        assert tree["s"]["n"] == "5"
        assert isinstance(tree["s"]["n"], str)
        assert tree["s"]["b"] == "true"

    def test_key_case_preserved(self, write):
        p = write("a.ini", "[s]\nMixedCase = 1\n")
        tree = ini_parser.load(str(p))
        assert "MixedCase" in tree["s"]

    def test_default_section_inherited(self, write):
        p = write("a.ini", "[DEFAULT]\nshared = 1\n\n[s]\nown = 2\n")
        tree = ini_parser.load(str(p))
        assert tree["DEFAULT"] == {"shared": "1"}
        assert tree["s"] == {"shared": "1", "own": "2"}

    def test_key_outside_section_is_error(self, write):
        p = write("bad.ini", "foo = bar\n")
        with pytest.raises(ParseError):
            ini_parser.load(str(p))


class TestEnvParser:
    def test_basic_and_export(self, write):
        p = write(".env", "FOO=bar\nexport BAZ=qux\n")
        assert env_parser.load(str(p)) == {"FOO": "bar", "BAZ": "qux"}

    def test_double_quoted_with_escapes(self, write):
        p = write(".env", 'FOO="line1\\nline2"\n')
        tree = env_parser.load(str(p))
        assert tree["FOO"] == "line1\nline2"

    def test_single_quoted_is_literal(self, write):
        p = write(".env", "FOO='no $expansion \\n here'\n")
        tree = env_parser.load(str(p))
        assert tree["FOO"] == "no $expansion \\n here"

    def test_full_line_comment_and_blank_lines(self, write):
        p = write(".env", "# a comment\n\nFOO=bar\n\n# trailing\n")
        assert env_parser.load(str(p)) == {"FOO": "bar"}

    def test_trailing_comment_on_unquoted_value(self, write):
        p = write(".env", "FOO=bar # a note\n")
        tree = env_parser.load(str(p))
        assert tree["FOO"] == "bar"

    def test_unspaced_hash_not_treated_as_comment(self, write):
        p = write(".env", "FOO=a#b\n")
        tree = env_parser.load(str(p))
        assert tree["FOO"] == "a#b"

    def test_quoted_value_can_contain_hash(self, write):
        p = write(".env", 'FOO="a#b"\n')
        tree = env_parser.load(str(p))
        assert tree["FOO"] == "a#b"

    def test_empty_value(self, write):
        p = write(".env", "FOO=\n")
        assert env_parser.load(str(p)) == {"FOO": ""}

    def test_values_always_strings(self, write):
        p = write(".env", "NUM=5\nBOOL=true\n")
        tree = env_parser.load(str(p))
        assert tree["NUM"] == "5" and isinstance(tree["NUM"], str)
        assert tree["BOOL"] == "true" and isinstance(tree["BOOL"], str)

    def test_invalid_line_reports_line_number(self, write):
        p = write(".env", "FOO=bar\nnot a valid line\n")
        with pytest.raises(ParseError) as exc:
            env_parser.load(str(p))
        assert exc.value.line == 2

    def test_unterminated_quote_is_error(self, write):
        p = write(".env", 'FOO="unterminated\n')
        with pytest.raises(ParseError):
            env_parser.load(str(p))
