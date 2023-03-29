"""Unit tests for the hyalus.utils.typing_utils module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from types import NoneType, GenericAlias

import pytest

from hyalus.utils import typing_utils


class TestTypeString:
    """Tests for the type_string utility method"""

    def test_int(self):
        """Test that a string with an integer value is converted to an integer"""
        assert typing_utils.type_string("1") == 1
        assert typing_utils.type_string("0") == 0
        assert typing_utils.type_string("-1") == -1

    def test_float(self):
        """Test that a string with an float value is converted to an float"""
        assert typing_utils.type_string("1.0") == 1.0
        assert typing_utils.type_string("0.0") == 0.0
        assert typing_utils.type_string("-1.0") == -1.0

    def test_bool(self):
        """Test that a string with an bool value is converted to an bool"""
        assert typing_utils.type_string("True") is True
        assert typing_utils.type_string("False") is False
        assert typing_utils.type_string("tRUe") is True
        assert typing_utils.type_string("fALsE") is False

    def test_string(self):
        """Test that something that cannot be cast as int/float/bool remains a string"""
        assert typing_utils.type_string("a string") == "a string"
        assert typing_utils.type_string("1 burrito") == "1 burrito"


class TestTypeCheck:
    """Tests for the type_check utility method"""

    def test_non_generic(self):
        """Test proper handling of non-generic types"""
        assert typing_utils.type_check(3, int)
        assert typing_utils.type_check(3.0, float)
        assert typing_utils.type_check(None, NoneType)
        assert typing_utils.type_check(True, bool)
        assert typing_utils.type_check("hi", str)
        assert typing_utils.type_check([1], list)
        assert typing_utils.type_check({1: 1}, dict)
        assert typing_utils.type_check({1}, set)
        assert typing_utils.type_check((1, 1), tuple)

    def test_different_origins(self):
        """Test that types with a different origin/container are treated as different"""
        assert not typing_utils.type_check([1], dict[int, int])
        assert not typing_utils.type_check([1], set[int])
        assert not typing_utils.type_check([1], tuple[int])
        assert not typing_utils.type_check({1}, list[int])

    def test_list_generics(self):
        """Test that list generics are properly type checked"""
        assert typing_utils.type_check([1, 2, 3], list[int])
        assert not typing_utils.type_check([1, 2, 3], list[str])
        assert typing_utils.type_check(["1", "2", "3"], list[str])
        assert not typing_utils.type_check(["1", "2", "3"], list[int])
        assert not typing_utils.type_check([1, 2, "3"], list[int])
        assert not typing_utils.type_check([1, 2, "3"], list[str])
        assert typing_utils.type_check([1, 2, "3"], list[int | str])
        assert not typing_utils.type_check([], list[int])

    def test_set_generics(self):
        """Test that set generics are properly type checked"""
        assert typing_utils.type_check({1, 2, 3}, set[int])
        assert not typing_utils.type_check({1, 2, 3}, set[str])
        assert typing_utils.type_check({"1", "2", "3"}, set[str])
        assert not typing_utils.type_check({"1", "2", "3"}, set[int])
        assert not typing_utils.type_check({1, 2, "3"}, set[int])
        assert not typing_utils.type_check({1, 2, "3"}, set[str])
        assert typing_utils.type_check({1, 2, "3"}, set[int | str])
        assert not typing_utils.type_check(set(), set[int])

    def test_tuple_generics(self):
        """Test that tuple generics are properly type checked"""
        assert typing_utils.type_check((1,), tuple[int])
        assert typing_utils.type_check((1, 1.0, "1"), tuple[int, float, str])
        assert not typing_utils.type_check((1, 1.0, "1"), tuple[int, float, int])
        assert not typing_utils.type_check((), tuple[int])

    def test_dict_generics(self):
        """Test that dict generics are properly type checked"""
        assert typing_utils.type_check({1: 1}, dict[int, int])
        assert typing_utils.type_check({1: "1"}, dict[int, str])
        assert not typing_utils.type_check({1: 1, 2: "2"}, dict[int, int])
        assert not typing_utils.type_check({}, dict[int, int])

    def test_unsupported_generic(self):
        """Test that a ValueError is raised if an unsupported generic is given as a type"""
        with pytest.raises(ValueError):
            typing_utils.type_check(3, GenericAlias(int, int))

    def test_sub_generics(self):
        """Test handling of cases of elements of a generic being other generics"""
        assert typing_utils.type_check([(1, "2"), (3, "4")], list[tuple[int, str]])
        assert typing_utils.type_check({(1, 2): [[3]], (4, 5): [[6]]}, dict[tuple[int, int], list[list[int]]])
        assert not typing_utils.type_check({(1, "2"): [3]}, dict[tuple[int, int], list[int]])
