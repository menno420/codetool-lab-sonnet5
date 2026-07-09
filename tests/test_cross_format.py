"""Cross-format equivalence: the same logical config expressed in each format
that can represent it, and the coercion policy that makes string-only
formats (INI/.env) comparable to natively-typed ones (JSON/YAML/TOML).

Note the "when it can be" qualifier from the spec: INI requires at least one
``[section]`` and has no nesting beyond section -> key, and ``.env`` has no
nesting at all. So a single identical *nested* structure can be shared by
JSON/YAML/TOML, but INI/.env equivalence is demonstrated against a
same-shaped subset (one section's worth of flat keys) instead -- that's a
structural property of those formats, not a cfgdiff limitation.
"""

from __future__ import annotations

from cfgdiff.diff import coerce_tree, diff_trees
from cfgdiff.parsers import ini_parser, json_parser, toml_parser, yaml_parser

NESTED = {"app": {"name": "myapp", "port": 8080, "debug": True, "tags": ["a", "b"]}}

JSON_TEXT = """{
  "app": {
    "name": "myapp",
    "port": 8080,
    "debug": true,
    "tags": ["a", "b"]
  }
}
"""

YAML_TEXT = """app:
  name: myapp
  port: 8080
  debug: true
  tags:
    - a
    - b
"""

TOML_TEXT = """[app]
name = "myapp"
port = 8080
debug = true
tags = ["a", "b"]
"""

FLAT = {"name": "myapp", "port": "8080", "debug": "true"}

INI_TEXT = """[app]
name = myapp
port = 8080
debug = true
"""

ENV_TEXT = """NAME=myapp
PORT=8080
DEBUG=true
"""


class TestFiveFormatEquivalence:
    def test_json_matches_reference(self, write):
        p = write("a.json", JSON_TEXT)
        assert json_parser.load(str(p)) == NESTED

    def test_yaml_matches_reference(self, write):
        p = write("a.yaml", YAML_TEXT)
        assert yaml_parser.load(str(p)) == NESTED

    def test_toml_matches_reference(self, write):
        p = write("a.toml", TOML_TEXT)
        assert toml_parser.load(str(p)) == NESTED

    def test_json_yaml_toml_pairwise_no_diff(self, write):
        pj = write("a.json", JSON_TEXT)
        py = write("a.yaml", YAML_TEXT)
        pt = write("a.toml", TOML_TEXT)
        tj, ty, tt = (
            json_parser.load(str(pj)),
            yaml_parser.load(str(py)),
            toml_parser.load(str(pt)),
        )
        assert diff_trees(tj, ty) == []
        assert diff_trees(ty, tt) == []
        assert diff_trees(tj, tt) == []

    def test_ini_matches_flat_reference(self, write):
        p = write("a.ini", INI_TEXT)
        tree = ini_parser.load(str(p))
        assert tree["app"] == FLAT

    def test_env_matches_flat_reference(self, write):
        from cfgdiff.parsers import env_parser

        p = write(".env", ENV_TEXT)
        assert env_parser.load(str(p)) == {"NAME": "myapp", "PORT": "8080", "DEBUG": "true"}

    def test_ini_and_env_equivalent_after_coercion(self, write):
        from cfgdiff.parsers import env_parser

        ini_tree = ini_parser.load(str(write("a.ini", INI_TEXT)))
        env_tree = env_parser.load(str(write(".env", ENV_TEXT)))

        # Different key case (ini: "name", env: "NAME") -- normalize case for
        # this comparison since env-var convention is uppercase while our INI
        # sample uses lowercase; that's a naming convention, not a semantic
        # difference cfgdiff itself resolves.
        ini_flat = {k.lower(): v for k, v in ini_tree["app"].items()}
        env_flat = {k.lower(): v for k, v in env_tree.items()}
        assert diff_trees(coerce_tree(ini_flat), coerce_tree(env_flat)) == []

    def test_flat_ini_section_matches_nested_app_after_coercion(self, write):
        ini_tree = ini_parser.load(str(write("a.ini", INI_TEXT)))
        coerced = coerce_tree(ini_tree["app"])
        # NESTED["app"] also has a "tags" list that plain INI can't represent;
        # compare only the keys INI *can* represent.
        subset = {k: v for k, v in NESTED["app"].items() if k != "tags"}
        assert diff_trees(coerced, subset) == []


class TestIniTypeCoercionPolicy:
    def test_ini_string_vs_yaml_native_no_coercion_shows_type_changed(self, write):
        ini_tree = ini_parser.load(str(write("a.ini", "[s]\nn = 5\n")))
        yaml_tree = {"s": {"n": 5}}
        # Without coercion (raw ini vs yaml), everything looks type-changed.
        entries = diff_trees(ini_tree, yaml_tree)
        assert entries[0].kind == "type_changed"

    def test_ini_string_vs_yaml_native_with_coercion_matches(self, write):
        ini_tree = ini_parser.load(str(write("a.ini", "[s]\nn = 5\nb = true\nf = 1.5\n")))
        yaml_tree = {"s": {"n": 5, "b": True, "f": 1.5}}
        assert diff_trees(coerce_tree(ini_tree), yaml_tree) == []

    def test_both_string_only_formats_no_coercion_needed(self, write):
        ini_tree = ini_parser.load(str(write("a.ini", "[s]\nn = 5\n")))

        env_tree = {"n": "5"}
        # ini nested under section vs flat env -- compare the inner dict directly
        assert diff_trees(ini_tree["s"], env_tree) == []
