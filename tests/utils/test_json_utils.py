"""Unit tests for the hyalus.utils.json module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import pytest

from hyalus.utils import json_utils


@pytest.fixture(name="test_array")
def fixture_test_array():
    """Example array for testing json util functionality"""
    return [1, {"2": 3}, {"4": {"5": [6]}}, [[7], 8]]


@pytest.fixture(name="test_object")
def fixture_test_object():
    """Example object for testing json util functionality"""
    return {"1": 2, "3": {"4": 5, "6": {"7": [8]}}}


class TestJsonGet:
    """Unit tests for the json_get utility function"""

    def test_json_get_array_1(self, test_array):
        """Test getting value from outer-most level of array"""
        assert json_utils.json_get(test_array, [0]) == 1
        assert json_utils.json_get(test_array, [1]) == {"2": 3}
        assert json_utils.json_get(test_array, [2]) == {"4": {"5": [6]}}

    def test_json_get_array_2(self, test_array):
        """Test getting value from inner levels of array"""
        assert json_utils.json_get(test_array, [1, "2"]) == 3
        assert json_utils.json_get(test_array, [2, "4"]) == {"5": [6]}
        assert json_utils.json_get(test_array, [2, "4", "5"]) == [6]

    def test_json_get_array_empty_path_list(self, test_array):
        """Test getting value when given an empty path list returns obj itself"""
        assert json_utils.json_get(test_array, []) == test_array

    def test_json_get_array_empty_array_pass(self):
        """Test getting value on empty array when not given a list of paths to process returns empty array"""
        assert json_utils.json_get([], []) == []

    def test_json_get_array_empty_array_fail(self):
        """Test getting value raises an IndexError when given an empty array as input with an index to process"""
        with pytest.raises(IndexError):
            json_utils.json_get([], [0])

    def test_json_get_array_invalid_index(self, test_array):
        """Test getting value raises an IndexError when given an index that does not exist"""
        with pytest.raises(IndexError):
            json_utils.json_get(test_array, [4])

    def test_json_get_object_1(self, test_object):
        """Test getting value from outer-most level of object"""
        assert json_utils.json_get(test_object, ["1"]) == 2
        assert json_utils.json_get(test_object, ["3"]) == {"4": 5, "6": {"7": [8]}}

    def test_json_get_object_2(self, test_object):
        """Test getting value from inner levels of object"""
        assert json_utils.json_get(test_object, ["3", "4"]) == 5
        assert json_utils.json_get(test_object, ["3", "6"]) == {"7": [8]}
        assert json_utils.json_get(test_object, ["3", "6", "7"]) == [8]
        assert json_utils.json_get(test_object, ["3", "6", "7", 0]) == 8

    def test_json_get_object_empty_path_list(self, test_object):
        """Test getting value when given an empty path list returns obj itself"""
        assert json_utils.json_get(test_object, []) == test_object

    def test_json_get_object_empty_object_pass(self):
        """Test getting value on empty object when not given a list of paths to process returns empty object"""
        assert json_utils.json_get({}, []) == {}

    def test_json_get_object_empty_object_fail(self):
        """Test getting value raises a KeyError when given an empty object as input with a key to process"""
        with pytest.raises(KeyError):
            json_utils.json_get({}, ["0"])

    def test_json_get_object_invalid_key(self, test_object):
        """Test getting value raises an KeyError when given a key that does not exist"""
        with pytest.raises(KeyError):
            json_utils.json_get(test_object, ["0"])


class TestJsonSet:
    """Unit tests for the json_set utility function"""

    def test_json_set_array_1(self, test_array):
        """Test setting value at outer-most level of array"""
        json_utils.json_set(test_array, [0], 10)
        assert test_array[0] == 10

    def test_json_set_array_2(self, test_array):
        """Test setting value at middle level of array"""
        json_utils.json_set(test_array, [3, 1], 10)
        assert test_array[3] == [[7], 10]

    def test_json_set_array_3(self, test_array):
        """Test setting value at inner-most level of array"""
        json_utils.json_set(test_array, [2, "4", "5", 0], 10)
        assert test_array[2]["4"]["5"][0] == 10

    def test_json_set_array_empty_path_list(self, test_array):
        """Test that attempting to set a value when giving an empty path list raises a ValueError"""
        with pytest.raises(ValueError):
            json_utils.json_set(test_array, [], 10)

    def test_json_set_array_invalid_index(self, test_array):
        """Test that attempting to set a value when giving an index that doesn't exist raises an IndexError"""
        with pytest.raises(IndexError):
            json_utils.json_set(test_array, [4], 10)

    def test_json_set_object_1(self, test_object):
        """Test setting value at outer-most level of object"""
        json_utils.json_set(test_object, ["1"], 10)
        assert test_object["1"] == 10

    def test_json_set_object_2(self, test_object):
        """Test setting value at an inner level of object"""
        json_utils.json_set(test_object, ["3", "6", "7"], 10)
        assert test_object["3"]["6"]["7"] == 10

    def test_json_set_object_empty_path_list(self, test_object):
        """Test that attempting to set a value when giving an empty path list raises a ValueError"""
        with pytest.raises(ValueError):
            json_utils.json_set(test_object, [], 10)

    def test_json_set_object_invalid_key(self, test_object):
        """Test that attempting to set a value when giving a key that does not exist raises a KeyError"""
        with pytest.raises(KeyError):
            json_utils.json_set(test_object, ["5"], 10)

    def test_json_set_object_create_key_true(self, test_object):
        """Test that when giving a key that does not exist and create_key is set to True, the object is updated"""
        json_utils.json_set(test_object, ["5"], 10, create_key=True)
        assert test_object["5"] == 10


class TestJsonAppend:
    """Unit tests for the json_append utility function"""

    def test_json_append_1(self, test_array):
        """Test appending to an outer array"""
        json_utils.json_append(test_array, [], 10)
        assert test_array[-1] == 10

    def test_json_append_2(self, test_array):
        """Test appending to an inner array"""
        json_utils.json_append(test_array, [3, 0], 10)
        assert test_array[3][0][-1] == 10

    def test_json_append_invalid_index(self, test_array):
        """Assert an IndexError is raised when path_list contains an index that doesn't exist"""
        with pytest.raises(IndexError):
            json_utils.json_append(test_array, [5], 10)

    def test_json_append_invalid_key(self, test_array):
        """Assert a KeyError is raised when path_list contains a key that doesn't exist"""
        with pytest.raises(KeyError):
            json_utils.json_append(test_array, [1, "5"], 10)

    def test_json_append_not_array(self, test_array):
        """Assert a ValueError is raised when trying to append a value to something that is not an array"""
        with pytest.raises(ValueError):
            json_utils.json_append(test_array, [1], 10)
