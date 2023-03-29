"""Unit tests for the hyalus.parse.tsv module"""
# pylint: disable=too-few-public-methods

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.parse import tsv


class TestTSVDataFrameParser:
    """Unit tests for the TSVDataFrameParser class - DataFrameParser specifics are out of scope"""

    def test_delimiter(self):
        """Assert the delimiter is set to a tab"""
        assert tsv.TSVDataFrameParser("path/to/file.tsv").delimiter == '\t'


class TestTSVKeyValueParser:
    """Unit tests for the TSVKeyValueParser class - KeyValueParser specifics are out of scope"""

    def test_delimiter(self):
        """Assert the delimiter is set to a tab"""
        assert tsv.TSVKeyValueParser("path/to/file.tsv").delimiter == '\t'
