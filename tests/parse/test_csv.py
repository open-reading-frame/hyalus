"""Unit tests for the hyalus.parse.csv module"""
# pylint: disable=too-few-public-methods

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.parse import csv


class TestCSVDataFrameParser:
    """Unit tests for the CSVDataFrameParser class - DataFrameParser specifics are out of scope"""

    def test_delimiter(self):
        """Assert the delimiter is set to a tab"""
        assert csv.CSVDataFrameParser("path/to/file.csv").delimiter == ','


class TestCSVKeyValueParser:
    """Unit tests for the CSVKeyValueParser class - KeyValueParser specifics are out of scope"""

    def test_delimiter(self):
        """Assert the delimiter is set to a tab"""
        assert csv.CSVKeyValueParser("path/to/file.csv").delimiter == ','
