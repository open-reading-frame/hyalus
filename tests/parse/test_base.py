"""Unit tests for the hyalus.parse.base module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
import shutil

import pandas as pd
import pytest

from hyalus.parse import base
from hyalus.parse.tsv import TSVDataFrameParser, TSVKeyValueParser

DATA_PATH = Path(__file__).parent / "data"
TSV_DF_1 = DATA_PATH / "example_df_1.tsv"
TSV_DF_2 = DATA_PATH / "example_df_2.tsv"
TSV_KV_1 = DATA_PATH / "example_kv_1.tsv"
TSV_KV_2 = DATA_PATH / "example_kv_2.tsv"


@pytest.fixture(name="tmp_tsv_df")
def fixture_tmp_tsv_df(tmp_path):
    """Copy TSV DataFrame to temp directory and return path to it"""
    shutil.copy2(TSV_DF_1, tmp_path)
    return tmp_path / "example_df_1.tsv"


@pytest.fixture(name="tmp_tsv_kv")
def fixture_tmp_tsv_kv(tmp_path):
    """Copy TSV key/value file to temp directory and return path to it"""
    shutil.copy2(TSV_KV_1, tmp_path)
    return tmp_path / "example_kv_1.tsv"


class TestResultsParser:
    """Unit tests for the ResultsParser base class functionality"""

    def test_abc_honored(self):
        """Assert that the ResultsParser class cannot be instantiated"""
        with pytest.raises(TypeError):
            base.ResultsParser("example_kv_1.tsv")  # pylint: disable=abstract-class-instantiated

    def test_use_glob_true(self):
        """Test integration of globbing functionality when giving a valid wildcard"""
        parser = TSVKeyValueParser(DATA_PATH / "*kv_1.tsv", use_glob=True)
        assert parser.file_path == DATA_PATH / "example_kv_1.tsv"

    def test_parse_cache_on(self):
        """Assert that parsing functions as expected and results are cached as expected when turned on"""
        parser = TSVKeyValueParser(DATA_PATH / "example_kv_1.tsv", cache=True)

        assert parser.parse() is parser.parse()

    def test_parse_cache_off(self):
        """Assert that parsing functions as expected and results are not cached when turned off"""
        parser = TSVKeyValueParser(DATA_PATH / "example_kv_1.tsv", cache=False)

        assert parser.parse() == parser.parse()
        assert parser.parse() is not parser.parse()


class TestDataFrameParser:
    """Unit tests for the DataFrameParser base class functionality"""

    def test_abc_honored(self):
        """Assert that the DataFrameParser class cannot be instantiated"""
        with pytest.raises(TypeError):
            base.DataFrameParser("example_df_1.tsv")  # pylint: disable=abstract-class-instantiated

    def test_parse(self):
        """Assert that an input file is properly parsed into a DataFrame"""
        parser = TSVDataFrameParser(DATA_PATH / "example_df_1.tsv")
        expected = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]], columns=["col1", "col2", "col3"])

        assert expected.equals(parser.parse())

    def test_parse_kwargs(self):
        """Assert that kwargs are properly passed into the ``pd.read_csv`` call"""
        parser = TSVDataFrameParser(DATA_PATH / "example_df_1.tsv", header=0, names=["a", "b", "c"])
        expected = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]], columns=["a", "b", "c"])

        assert expected.equals(parser.parse())

    def test_eq_true_file_path(self):
        """Assert that two parsers with the same file path are treated as equal"""
        assert TSVDataFrameParser("path/to/file.tsv") == TSVDataFrameParser("path/to/file.tsv")

    def test_eq_true_parse(self, tmp_tsv_df):
        """Assert that two parsers with different file paths but the same parsed content are treated as equal"""
        assert TSVDataFrameParser(tmp_tsv_df) == TSVDataFrameParser(TSV_DF_1)

    def test_eq_false(self):
        """Assert that two parsers with different file paths and different content are treated as unequal"""
        assert TSVDataFrameParser(TSV_DF_1) != TSVDataFrameParser(TSV_DF_2)

    def test_search(self):
        """Test subsetting of DataFrame with one valid constraint"""
        expected = pd.DataFrame([[1, 2, 3]], columns=["col1", "col2", "col3"])
        assert TSVDataFrameParser(TSV_DF_1).search(("col1", 1)).equals(expected)

    def test_search_multiple(self):
        """Test subsetting of DataFrame with multiple valid constraints"""
        expected = pd.DataFrame([[1, 2, 3]], columns=["col1", "col2", "col3"])
        assert TSVDataFrameParser(TSV_DF_1).search([("col1", 1), ("col2", 2)]).equals(expected)


class TestKeyValueParser:
    """Unit tests for the KeyValueParser base class functionality"""

    def test_abc_honored(self):
        """Assert that the KeyValueParser class cannot be instantiated"""
        with pytest.raises(TypeError):
            base.KeyValueParser("example_kv_1.tsv")  # pylint: disable=abstract-class-instantiated

    def test_parse(self):
        """Assert that an input file is properly parsed into a dictionary of key-value pairs"""
        parser = TSVKeyValueParser(DATA_PATH / "example_kv_1.tsv")
        expected = {"key1": "value1", "key2": "value2\tmore\ntext", "key3\twith delim": "value3\t'after the delimiter'"}

        assert expected == parser.parse()

    def test_eq_true_file_path(self):
        """Assert that two parsers with the same file path are treated as equal"""
        assert TSVKeyValueParser("path/to/file.tsv") == TSVKeyValueParser("path/to/file.tsv")

    def test_eq_true_parse(self, tmp_tsv_kv):
        """Assert that two parsers with different file paths but the same content are treated as equal"""
        assert TSVKeyValueParser(tmp_tsv_kv) == TSVKeyValueParser(TSV_KV_1)

    def test_eq_false(self):
        """Assert that two parsers with different file paths and different content are treated as unequal"""
        assert TSVKeyValueParser(TSV_KV_1) != TSVKeyValueParser(TSV_KV_2)

    def test_search(self):
        """Test searching for a given key"""
        assert TSVKeyValueParser(TSV_KV_1).search("key1") == "value1"
