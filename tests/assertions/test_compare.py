"""Unit tests for the hyalus.assert.compare module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import pandas as pd
import pytest

from hyalus.assertions import compare


@pytest.fixture(name="example_list")
def fixture_example_list():
    """Example list for containment checks"""
    return [1, "two", (3,)]


@pytest.fixture(name="example_dict")
def fixture_example_dict():
    """Example dict for keys/items/values containment checks"""
    return {"one": 2, 3: "four", (5,): (6,)}


@pytest.fixture(name="example_df")
def fixture_example_df():
    """Example DataFrame for containment checks"""
    return pd.DataFrame([[1, 2, 3], [4, 5, 3]], columns=["col1", "col2", "col3"])


def test_eq_true():
    """Test case for the ``compare.eq`` function where the test result should be True"""
    assert compare.eq(4, 4, 4, 4)


def test_eq_false():
    """Test case for the ``compare.eq`` function where the test result should be False"""
    assert not compare.eq(4, 4, 3, 4)


def test_eq_no_args():
    """Test case for the ``compare.eq`` function where no arguments are given, should be True"""
    assert compare.eq()


def test_eq_one_arg():
    """Test case for the ``compare.eq`` function where a single argument is given, should be True"""
    assert compare.eq(1)


def test_ne_true():
    """Test case for the ``compare.ne`` function where the test result should be True"""
    assert compare.ne(1, 2, 3, 4, {1})


def test_ne_false():
    """Test case for the ``compare.ne`` function where the test result should be False"""
    assert not compare.ne(1, 2, 3, 3, {1})


def test_ne_no_args():
    """Test case for the ``compare.ne`` function where no arguments are given, should be True"""
    assert compare.ne()


def test_ne_one_arg():
    """Test case for the ``compare.ne`` function where a single argument is given, should be True"""
    assert compare.ne(1)


def test_gt_true():
    """Test case for the ``compare.gt`` function where the test result should be True"""
    assert compare.gt(4, 3, 2, 1)


def test_gt_false():
    """Test case for the ``compare.gt`` function where the test result should be False"""
    assert not compare.gt(4, 3, 2, 2)


def test_gt_no_args():
    """Test case for the ``compare.gt`` function where no arguments are given, should be True"""
    assert compare.gt()


def test_gt_one_arg():
    """Test case for the ``compare.gt`` function where a single argument is given, should be True"""
    assert compare.gt(1)


def test_ge_true():
    """Test case for the ``compare.ge`` function where the test result should be True"""
    assert compare.ge(4, 4, 3, 2, 2, 1)


def test_ge_false():
    """Test case for the ``compare.ge`` function where the test result should be False"""
    assert not compare.ge(4, 5, 3, 2, 1)


def test_ge_no_args():
    """Test case for the ``compare.ge`` function where no arguments are given, should be True"""
    assert compare.ge()


def test_ge_one_arg():
    """Test case for the ``compare.ge`` function where a single argument is given, should be True"""
    assert compare.ge(1)


def test_lt_true():
    """Test case for the ``compare.lt`` function where the test result should be True"""
    assert compare.lt(1, 2, 3, 4)


def test_lt_false():
    """Test case for the ``compare.lt`` function where the test result should be False"""
    assert not compare.lt(1, 2, 3, 3)


def test_lt_no_args():
    """Test case for the ``compare.lt`` function where no arguments are given, should be True"""
    assert compare.lt()


def test_lt_one_arg():
    """Test case for the ``compare.lt`` function where a single argument is given, should be True"""
    assert compare.lt(1)


def test_le_true():
    """Test case for the ``compare.le`` function where the test result should be True"""
    assert compare.le(1, 1, 2, 3, 4, 4)


def test_le_false():
    """Test case for the ``compare.le`` function where the test result should be False"""
    assert not compare.le(2, 2, 3, 2, 3, 3)


def test_le_no_args():
    """Test case for the ``compare.le`` function where no arguments are given, should be True"""
    assert compare.le()


def test_le_one_arg():
    """Test case for the ``compare.le`` function where a single argument is given, should be True"""
    assert compare.le(1)


def test_is_true():
    """Test case for the ``compare.is_`` function where the test result should be True"""
    obj = object()

    assert compare.is_(obj, obj, obj, obj)


def test_is_false():
    """Test case for the ``compare.is_`` function where the test result should be False"""
    obj1 = object()
    obj2 = object()

    assert not compare.is_(obj1, obj1, obj2, obj1)


def test_is_no_args():
    """Test case for the ``compare.is_`` function where no arguments are given, should be True"""
    assert compare.is_()


def test_is_one_arg():
    """Test case for the ``compare.is_`` function where a single argument is given, should be True"""
    assert compare.is_(object())


def test_is_not_true():
    """Test case for the ``compare.is_not`` function where the test result should be True"""
    obj1 = object()
    obj2 = object()
    obj3 = object()

    assert compare.is_not(obj1, obj2, obj3)


def test_is_not_false():
    """Test case for the ``compare.is_not`` function where the test result should be False"""
    obj1 = object()
    obj2 = object()

    assert not compare.is_not(obj1, obj2, obj1)


def test_is_not_no_args():
    """Test case for the ``compare.is_not`` function where no arguments are given, should be True"""
    assert compare.is_not()


def test_is_not_one_arg():
    """Test case for the ``compare.is_not`` function where a single argument is given, should be True"""
    assert compare.is_not(object())


def test_in_true(example_list):
    """Simple test case for the ``compare.in_`` function where the test result should be True"""
    assert compare.in_(1, example_list)


def test_in_false(example_list):
    """Simple test case for the ``compare.in_`` function where the test result should be False"""
    assert not compare.in_(4, example_list)


def test_not_in_true(example_list):
    """Simple test case for the ``compare.not_in`` function where the test result should be True"""
    assert compare.not_in(4, example_list)


def test_not_in_false(example_list):
    """Simple test case for the ``compare.not_in`` function where the test result should be False"""
    assert not compare.not_in(1, example_list)


def test_contains_true(example_list):
    """Simple test case for the ``compare.contains`` function where the test result should be True"""
    assert compare.contains(example_list, 1)


def test_contains_false(example_list):
    """Simple test case for the ``compare.contains`` function where the test result should be False"""
    assert not compare.contains(example_list, 4)


def test_does_not_contain_true(example_list):
    """Simple test case for the ``compare.does_not_contain`` function where the test result should be True"""
    assert compare.does_not_contain(example_list, 4)


def test_does_not_contain_false(example_list):
    """Simple test case for the ``compare.does_not_contain`` function where the test result should be False"""
    assert not compare.does_not_contain(example_list, 1)


def test_keys_contain_true(example_dict):
    """Simple test case for the ``compare.keys_contain`` function where the test result should be True"""
    assert compare.keys_contain(example_dict, 3)


def test_keys_contain_false(example_dict):
    """Simple test case for the ``compare.keys_contain`` function where the test result should be False"""
    assert not compare.keys_contain(example_dict, 1)


def test_values_contain_true(example_dict):
    """Simple test case for the ``compare.values_contain`` function where the test result should be True"""
    assert compare.values_contain(example_dict, (6,))


def test_values_contain_false(example_dict):
    """Simple test case for the ``compare.values_contain`` function where the test result should be False"""
    assert not compare.values_contain(example_dict, "three")


def test_items_contain_true(example_dict):
    """Simple test case for the ``compare.items_contain`` function where the test result should be True"""
    assert compare.items_contain(example_dict, (3, "four"))


def test_items_contain_false(example_dict):
    """Simple test case for the ``compare.items_contain`` function where the test result should be False"""
    assert not compare.items_contain(example_dict, (1, "two"))


def test_dataframe_contains_true_1(example_df):
    """Test case for ``compare.dataframe_contains`` where the given criteria match one record"""
    assert compare.dataframe_contains(example_df, [("col1", 1), ("col2", 2), ("col3", 3)])


def test_dataframe_contains_true_2(example_df):
    """Test case for ``compare.dataframe_contains`` where the given criteria match more than one record"""
    assert compare.dataframe_contains(example_df, ("col3", 3))


def test_dataframe_contains_true_3(example_df):
    """Test case for ``compare.dataframe_contains`` where no criteria are given"""
    assert compare.dataframe_contains(example_df, [])


def test_dataframe_contains_false(example_df):
    """Test case for ``compare.dataframe_contains`` where the given criteria do not match any records"""
    assert not compare.dataframe_contains(example_df, [("col1", 1), ("col2", 5)])
