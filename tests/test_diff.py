from __future__ import annotations

from cfgdiff.diff import coerce_scalar, coerce_tree, diff_trees


def kinds(entries):
    return {(e.path, e.kind) for e in entries}


class TestNestedStructures:
    def test_three_levels_deep_no_diff(self):
        a = {"a": {"b": {"c": 1}}}
        b = {"a": {"b": {"c": 1}}}
        assert diff_trees(a, b) == []

    def test_three_levels_deep_changed_leaf(self):
        a = {"a": {"b": {"c": 1}}}
        b = {"a": {"b": {"c": 2}}}
        entries = diff_trees(a, b)
        assert len(entries) == 1
        assert entries[0].path == "a.b.c"
        assert entries[0].kind == "value_changed"

    def test_added_and_removed_nested_keys(self):
        a = {"a": {"b": 1, "c": 2}}
        b = {"a": {"b": 1, "d": 3}}
        result = kinds(diff_trees(a, b))
        assert ("a.c", "removed") in result
        assert ("a.d", "added") in result
        assert len(result) == 2


class TestTypeVsValueChanged:
    def test_value_changed_same_type(self):
        entries = diff_trees({"x": 5}, {"x": 6})
        assert entries[0].kind == "value_changed"

    def test_type_changed_str_vs_int(self):
        entries = diff_trees({"x": "5"}, {"x": 5})
        assert entries[0].kind == "type_changed"
        assert entries[0].old == "5"
        assert entries[0].new == 5

    def test_bool_not_conflated_with_int(self):
        # type(True) is bool, not int -- must be reported as a type change,
        # not silently treated as equal to 1 (Python's `True == 1` is True,
        # but that's not what a config-diff user wants to hear).
        entries = diff_trees({"x": True}, {"x": 1})
        assert entries[0].kind == "type_changed"

    def test_dict_vs_list_is_type_changed(self):
        entries = diff_trees({"x": {"a": 1}}, {"x": [1]})
        assert entries[0].kind == "type_changed"

    def test_float_vs_int_is_type_changed(self):
        entries = diff_trees({"x": 5}, {"x": 5.0})
        assert entries[0].kind == "type_changed"


class TestNullEmptyMissing:
    def test_null_equal_to_null(self):
        assert diff_trees({"x": None}, {"x": None}) == []

    def test_null_vs_value_is_type_changed(self):
        entries = diff_trees({"x": None}, {"x": 0})
        assert entries[0].kind == "type_changed"

    def test_empty_dict_equal(self):
        assert diff_trees({}, {}) == []

    def test_empty_list_equal(self):
        assert diff_trees({"x": []}, {"x": []}) == []

    def test_missing_key_is_added_or_removed_not_type_changed(self):
        entries = diff_trees({"a": 1}, {"b": 2})
        result = kinds(entries)
        assert ("a", "removed") in result
        assert ("b", "added") in result


class TestListDiffOrderMatters:
    def test_identical_lists_no_diff(self):
        assert diff_trees({"x": [1, 2, 3]}, {"x": [1, 2, 3]}) == []

    def test_reordered_list_is_reported_as_diff(self):
        # Documented policy: list order matters. [1, 2, 3] vs [3, 2, 1] is
        # NOT treated as a no-op reorder; it reports per-index differences.
        entries = diff_trees({"x": [1, 2, 3]}, {"x": [3, 2, 1]})
        paths = {e.path for e in entries}
        assert "x[0]" in paths and "x[2]" in paths
        assert "x[1]" not in paths  # middle element (2) unchanged by position

    def test_list_length_change_reports_added(self):
        entries = diff_trees({"x": [1, 2]}, {"x": [1, 2, 3]})
        assert len(entries) == 1
        assert entries[0].path == "x[2]"
        assert entries[0].kind == "added"
        assert entries[0].new == 3

    def test_list_length_change_reports_removed(self):
        entries = diff_trees({"x": [1, 2, 3]}, {"x": [1, 2]})
        assert len(entries) == 1
        assert entries[0].path == "x[2]"
        assert entries[0].kind == "removed"
        assert entries[0].old == 3

    def test_nested_list_of_dicts(self):
        a = {"x": [{"a": 1}, {"a": 2}]}
        b = {"x": [{"a": 1}, {"a": 3}]}
        entries = diff_trees(a, b)
        assert len(entries) == 1
        assert entries[0].path == "x[1].a"


class TestIgnore:
    def test_ignore_exact_path(self):
        entries = diff_trees({"a": 1, "b": 2}, {"a": 9, "b": 9}, ignore_prefixes=["a"])
        assert kinds(entries) == {("b", "value_changed")}

    def test_ignore_prefix_covers_children(self):
        a = {"server": {"host": "x", "port": 1}, "db": {"name": "n"}}
        b = {"server": {"host": "y", "port": 2}, "db": {"name": "m"}}
        entries = diff_trees(a, b, ignore_prefixes=["server"])
        assert kinds(entries) == {("db.name", "value_changed")}

    def test_ignore_does_not_match_sibling_with_shared_prefix_string(self):
        # "server" must not accidentally ignore "serverX" (segment-boundary match only)
        a = {"server": {"x": 1}, "serverX": {"x": 1}}
        b = {"server": {"x": 2}, "serverX": {"x": 2}}
        entries = diff_trees(a, b, ignore_prefixes=["server"])
        assert kinds(entries) == {("serverX.x", "value_changed")}

    def test_ignore_list_index_path(self):
        entries = diff_trees({"x": [1, 2]}, {"x": [1, 9]}, ignore_prefixes=["x[1]"])
        assert entries == []


class TestCoercion:
    def test_coerce_scalar_bool(self):
        assert coerce_scalar("true") is True
        assert coerce_scalar("False") is False
        assert coerce_scalar("TRUE") is True

    def test_coerce_scalar_int(self):
        assert coerce_scalar("5") == 5
        assert isinstance(coerce_scalar("5"), int)
        assert coerce_scalar("-3") == -3

    def test_coerce_scalar_float(self):
        assert coerce_scalar("5.5") == 5.5
        assert coerce_scalar("1e3") == 1000.0

    def test_coerce_scalar_leaves_non_coercible_strings(self):
        assert coerce_scalar("hello") == "hello"
        assert coerce_scalar("") == ""

    def test_coerce_scalar_passthrough_non_string(self):
        assert coerce_scalar(5) == 5
        assert coerce_scalar(None) is None

    def test_coerce_tree_recurses(self):
        tree = {"a": "5", "b": ["true", "x"], "c": {"d": "1.5"}}
        result = coerce_tree(tree)
        assert result == {"a": 5, "b": [True, "x"], "c": {"d": 1.5}}

    def test_coercion_enables_cross_format_equivalence(self):
        # simulates the CLI's policy: coerce the string-only side, then diff normally
        env_tree = {"port": "8080", "debug": "true"}
        yaml_tree = {"port": 8080, "debug": True}
        assert diff_trees(coerce_tree(env_tree), yaml_tree) == []

    def test_coercion_still_catches_real_type_mismatch(self):
        # "5" coerces to int 5, but the other side is a float 5.0 -> still type_changed
        env_tree = {"x": "5"}
        yaml_tree = {"x": 5.0}
        entries = diff_trees(coerce_tree(env_tree), yaml_tree)
        assert entries[0].kind == "type_changed"
