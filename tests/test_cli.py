from __future__ import annotations

import json


class TestExitCodes:
    def test_diff_identical_exits_0(self, run_cli, write):
        write("a.json", '{"a": 1}')
        write("b.json", '{"a": 1}')
        result = run_cli("diff", "a.json", "b.json")
        assert result.returncode == 0
        assert "no differences" in result.stdout

    def test_diff_with_differences_exits_1(self, run_cli, write):
        write("a.json", '{"a": 1}')
        write("b.json", '{"a": 2}')
        result = run_cli("diff", "a.json", "b.json")
        assert result.returncode == 1
        assert "a" in result.stdout

    def test_diff_missing_file_exits_2(self, run_cli, write):
        write("a.json", '{"a": 1}')
        result = run_cli("diff", "a.json", "nope.json")
        assert result.returncode == 2
        assert "cfgdiff: error:" in result.stderr

    def test_diff_parse_error_exits_2(self, run_cli, write):
        write("a.json", '{"a": 1}')
        write("bad.json", "{not valid json")
        result = run_cli("diff", "a.json", "bad.json")
        assert result.returncode == 2
        assert "bad.json" in result.stderr

    def test_validate_ok_exits_0(self, run_cli, write):
        write("a.json", '{"a": 1}')
        result = run_cli("validate", "a.json")
        assert result.returncode == 0
        assert "OK" in result.stdout

    def test_validate_bad_exits_2(self, run_cli, write):
        write("bad.json", "{not valid")
        result = run_cli("validate", "bad.json")
        assert result.returncode == 2

    def test_convert_success_exits_0(self, run_cli, write):
        write("a.json", '{"a": 1}')
        result = run_cli("convert", "a.json", "--to", "yaml")
        assert result.returncode == 0
        assert "a: 1" in result.stdout

    def test_unknown_format_exits_2(self, run_cli, write):
        write("a.weird", '{"a": 1}')
        result = run_cli("validate", "a.weird")
        assert result.returncode == 2


class TestJsonOutputShape:
    def test_output_json_is_list_of_entries(self, run_cli, write):
        write("a.json", '{"x": 1, "y": 2}')
        write("b.json", '{"x": 9, "z": 3}')
        result = run_cli("diff", "a.json", "b.json", "--output", "json")
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        assert isinstance(payload, list)
        for entry in payload:
            assert set(entry.keys()) == {"path", "kind", "old", "new"}
            assert entry["kind"] in {"added", "removed", "value_changed", "type_changed"}
        paths = {e["path"] for e in payload}
        assert paths == {"x", "y", "z"}

    def test_output_json_identical_is_empty_list(self, run_cli, write):
        write("a.json", '{"x": 1}')
        write("b.json", '{"x": 1}')
        result = run_cli("diff", "a.json", "b.json", "--output", "json")
        assert result.returncode == 0
        assert json.loads(result.stdout) == []


class TestIgnoreFlag:
    def test_ignore_repeatable(self, run_cli, write):
        write("a.json", '{"a": 1, "b": 2, "c": 3}')
        write("b.json", '{"a": 9, "b": 9, "c": 9}')
        result = run_cli("diff", "a.json", "b.json", "--ignore", "a", "--ignore", "b")
        assert result.returncode == 1
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        assert len(lines) == 1
        assert "~ c:" in lines[0]

    def test_ignore_all_diffs_yields_exit_0(self, run_cli, write):
        write("a.json", '{"a": 1}')
        write("b.json", '{"a": 2}')
        result = run_cli("diff", "a.json", "b.json", "--ignore", "a")
        assert result.returncode == 0


class TestNoColor:
    def test_no_color_has_no_ansi_codes(self, run_cli, write):
        write("a.json", '{"a": 1}')
        write("b.json", '{"a": 2}')
        result = run_cli("diff", "a.json", "b.json", "--no-color")
        assert "\033[" not in result.stdout


class TestConvertOutputFile:
    def test_convert_to_file(self, run_cli, write, tmp_path):
        write("a.json", '{"a": 1}')
        out = tmp_path / "out.yaml"
        result = run_cli("convert", "a.json", "--to", "yaml", "-o", str(out))
        assert result.returncode == 0
        assert out.exists()
        assert "a: 1" in out.read_text()
        assert result.stdout == ""

    def test_convert_warnings_go_to_stderr_not_fatal(self, run_cli, write):
        write("a.yaml", "a: null\n")
        result = run_cli("convert", "a.yaml", "--to", "json")
        assert result.returncode == 0
        assert '"a": null' in result.stdout

    def test_convert_none_to_toml_is_fatal(self, run_cli, write):
        write("a.yaml", "a: null\n")
        result = run_cli("convert", "a.yaml", "--to", "toml")
        assert result.returncode == 2
        assert "cfgdiff: error:" in result.stderr


class TestCrossFormatDiff:
    def test_yaml_vs_json_cross_format(self, run_cli, write):
        write("a.yaml", "server:\n  port: 8080\n")
        write("b.json", '{"server": {"port": 8080}}')
        result = run_cli("diff", "a.yaml", "b.json")
        assert result.returncode == 0

    def test_toml_vs_yaml_cross_format_with_diff(self, run_cli, write):
        write("a.toml", '[server]\nport = 8080\n')
        write("b.yaml", "server:\n  port: 9090\n")
        result = run_cli("diff", "a.toml", "b.yaml")
        assert result.returncode == 1
        assert "server.port" in result.stdout

    def test_format_override_flags(self, run_cli, write):
        # file named .conf-like but force json parsing via --format-a
        p = write("data.txt", '{"a": 1}')
        write("b.json", '{"a": 1}')
        result = run_cli("diff", str(p), "b.json", "--format-a", "json")
        assert result.returncode == 0


class TestHelp:
    def test_top_level_help(self, run_cli):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "diff" in result.stdout
        assert "convert" in result.stdout
        assert "validate" in result.stdout

    def test_diff_help(self, run_cli):
        result = run_cli("diff", "--help")
        assert result.returncode == 0
        assert "--ignore" in result.stdout
        assert "--output" in result.stdout

    def test_convert_help(self, run_cli):
        result = run_cli("convert", "--help")
        assert result.returncode == 0
        assert "--to" in result.stdout

    def test_validate_help(self, run_cli):
        result = run_cli("validate", "--help")
        assert result.returncode == 0
        assert "FILE" in result.stdout

    def test_version_flag(self, run_cli):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "0.1.1" in result.stdout
