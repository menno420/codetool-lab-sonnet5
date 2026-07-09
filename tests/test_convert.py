from __future__ import annotations

import datetime

import pytest

from cfgdiff.convert import to_json, to_toml, to_yaml
from cfgdiff.errors import ConvertError
from cfgdiff.parsers import json_parser, toml_parser, yaml_parser


class TestLosslessRoundTrips:
    def test_json_to_yaml_to_json_round_trip(self, write):
        tree = {"a": {"b": [1, 2, 3], "c": True, "d": None, "e": 1.5}}
        yaml_text = to_yaml(tree)
        p = write("out.yaml", yaml_text)
        assert yaml_parser.load(str(p)) == tree

    def test_yaml_to_json_to_yaml_round_trip(self, write):
        tree = {"a": {"b": [1, 2, 3], "c": False, "d": None}}
        json_text = to_json(tree)
        p = write("out.json", json_text)
        assert json_parser.load(str(p)) == tree

    def test_toml_to_json_to_toml_round_trip_no_datetime(self, write):
        tree = {"a": {"b": [1, 2, 3], "name": "x", "ok": True}}
        json_text = to_json(tree)
        p = write("out.json", json_text)
        assert json_parser.load(str(p)) == tree

    def test_json_to_toml_round_trip(self, write):
        tree = {"a": {"b": [1, 2, 3], "name": "x", "ok": True}}
        toml_text = to_toml(tree)
        p = write("out.toml", toml_text)
        assert toml_parser.load(str(p)) == tree

    def test_toml_datetime_round_trips_through_toml_and_yaml(self, write):
        tree = {"created": datetime.date(2024, 1, 1)}
        toml_text = to_toml(tree)
        p = write("out.toml", toml_text)
        assert toml_parser.load(str(p)) == tree

        yaml_text = to_yaml(tree)
        p2 = write("out.yaml", yaml_text)
        assert yaml_parser.load(str(p2)) == tree


class TestConvertWarnings:
    def test_shared_ref_warns(self):
        shared = {"x": 1}
        tree = {"a": shared, "b": shared}
        warnings = []
        to_json(tree, warnings.append)
        assert any("shared" in w for w in warnings)

    def test_no_warning_when_no_shared_refs(self):
        tree = {"a": {"x": 1}, "b": {"x": 1}}  # equal but NOT the same object
        warnings = []
        to_json(tree, warnings.append)
        assert warnings == []

    def test_non_string_key_stringified_and_warns(self):
        tree = {1: "a", "b": 2}
        warnings = []
        result = to_json(tree, warnings.append)
        assert '"1": "a"' in result
        assert any("non-string key" in w for w in warnings)

    def test_key_collision_after_stringification_warns(self):
        tree = {1: "int-key", "1": "str-key"}
        warnings = []
        to_json(tree, warnings.append)
        assert any("collision" in w for w in warnings)

    def test_datetime_to_json_warns_and_stringifies(self):
        tree = {"created": datetime.date(2024, 1, 1)}
        warnings = []
        result = to_json(tree, warnings.append)
        assert '"2024-01-01"' in result
        assert any("datetime" in w for w in warnings)

    def test_datetime_to_toml_does_not_warn(self):
        tree = {"created": datetime.date(2024, 1, 1)}
        warnings = []
        to_toml(tree, warnings.append)
        assert not any("datetime" in w for w in warnings)

    def test_datetime_to_yaml_does_not_warn(self):
        tree = {"created": datetime.date(2024, 1, 1)}
        warnings = []
        to_yaml(tree, warnings.append)
        assert not any("datetime" in w for w in warnings)


class TestConvertHardErrors:
    def test_none_to_toml_is_error(self):
        with pytest.raises(ConvertError, match="null/None"):
            to_toml({"a": None})

    def test_none_nested_to_toml_is_error(self):
        with pytest.raises(ConvertError, match="null/None"):
            to_toml({"a": {"b": [1, None]}})

    def test_non_dict_root_to_toml_is_error(self):
        with pytest.raises(ConvertError, match="root"):
            to_toml([1, 2, 3])

    def test_scalar_root_to_toml_is_error(self):
        with pytest.raises(ConvertError):
            to_toml("just a string")

    def test_none_to_json_is_fine(self):
        assert to_json({"a": None}) == '{\n  "a": null\n}\n'

    def test_none_to_yaml_is_fine(self):
        assert "a: null" in to_yaml({"a": None}) or "a:" in to_yaml({"a": None})
