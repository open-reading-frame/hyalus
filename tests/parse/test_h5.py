"""Unit tests for the hyalus.parse.h5 module"""
# pylint: disable=unsubscriptable-object

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
import shutil

import pytest

import hyalus.parse.h5 as h5_parse

DATA_PATH = Path(__file__).parent / "data"
H5_1 = DATA_PATH / "example_1.h5"
H5_2 = DATA_PATH / "example_2.h5"


@pytest.fixture(name="tmp_h5")
def fixture_tmp_h5(tmp_path):
    """Copies H5_1 file to a temp directory and returns path to the file"""
    shutil.copy2(H5_1, tmp_path)
    return tmp_path / "example_1.h5"


@pytest.fixture(name="h5_file")
def fixture_h5_file(tmp_h5):
    """Returns a read-only File created from tmp_h5"""
    return h5_parse.File(tmp_h5, 'r')


class TestDataset:
    """Unit tests for the Dataset class"""

    def test_eq_true(self, h5_file):
        """Test Datasets that are identical are treated as equal"""
        assert h5_file["dataset_1"] == h5_file["dataset_1"]
        assert h5_file["/sub"]["dataset_2"] == h5_file["/sub"]["dataset_2"]
        assert h5_file["/sub/group"]["dataset_3"] == h5_file["/sub/group"]["dataset_3"]

    def test_eq_false_different_shape(self, h5_file):
        """Test Datasets that differ in shape are handled correctly and not treated as equal"""
        assert h5_file["dataset_1"] != h5_file["/sub"]["dataset_2"]
        assert h5_file["dataset_1"] != h5_file["/sub/group"]["dataset_3"]
        assert h5_file["/sub"]["dataset_2"] != h5_file["/sub/group"]["dataset_3"]

    def test_eq_false_different_items(self):
        """Test Datasets that differ in values are handled correctly and not treated as equal"""
        h5_file_1 = h5_parse.File(H5_1, 'r')
        h5_file_2 = h5_parse.File(H5_2, 'r')

        assert h5_file_1["dataset_1"] != h5_file_2["dataset_1"]
        assert h5_file_1["/sub"]["dataset_2"] != h5_file_2["/sub"]["dataset_2"]

    def test_eq_false_bad_type(self, h5_file):
        """Test that values that are not Datasets are not treated as equal"""
        assert h5_file["dataset_1"] != 2
        assert h5_file["dataset_1"] != "2"


class TestGroup:
    """Unit tests for the Group class"""

    def test_eq_true_simple(self, h5_file):
        """Test Group equality when no sub groups exist"""
        assert h5_file["/sub/group"] == h5_file["/sub/group"]

    def test_eq_true_subgroups(self, h5_file):
        """Test Group equality when sub groups do exist"""
        assert h5_file["/sub"] == h5_file["/sub"]

    def test_eq_false_different_groups(self):
        """Test Group inequality when sub groups are different"""
        h5_file_1 = h5_parse.File(H5_1, 'r')
        h5_file_2 = h5_parse.File(H5_2, 'r')

        assert h5_file_1["/sub"] != h5_file_2["/sub"]

    def test_eq_false_different_datasets(self):
        """Test Group inequality when datasets are different"""
        h5_file_1 = h5_parse.File(H5_1, 'r')
        h5_file_2 = h5_parse.File(H5_2, 'r')

        assert h5_file_1["/sub/group"] != h5_file_2["/sub/other"]

    def test_eq_false_bad_type(self, h5_file):
        """Test inequality when giving something other than a Group"""
        assert h5_file["/sub/group"] != 2


class TestH5Parser:
    """Unit tests for the H5Parser class"""

    def test_eq_true_file_path(self):
        """Assert that two parsers with the same file path are treated as equal"""
        assert h5_parse.H5Parser("path/to/file.h5") == h5_parse.H5Parser("path/to/file.h5")

    def test_eq_true_parse(self, tmp_h5):
        """Assert that two parsers with different file paths but the same parsed content are treated as equal"""
        assert h5_parse.H5Parser(tmp_h5) == h5_parse.H5Parser(H5_1)

    def test_eq_false(self):
        """Assert that two parsers with different file paths and different content are treated as unequal"""
        assert h5_parse.H5Parser(H5_1) != h5_parse.H5Parser(H5_2)

    def test_search(self):
        """Test searching through groups/datasets"""
        assert h5_parse.H5Parser(H5_1).search(["/sub/group", "dataset_3", 0, 1]) == 2
