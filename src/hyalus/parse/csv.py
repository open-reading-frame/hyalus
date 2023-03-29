"""CSV file parsers"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.parse.base import DataFrameParser, KeyValueParser


class CSVDataFrameParser(DataFrameParser):
    """Parser for CSV to pandas ``DataFrame``"""

    @property
    def delimiter(self) -> str:
        r""":return: ``','``"""
        return ','


class CSVKeyValueParser(KeyValueParser):
    """Key-value parser with commas as a delimiter"""

    @property
    def delimiter(self) -> str:
        r""":return: ``','``"""
        return ','
