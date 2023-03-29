"""TSV file parsers"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.parse.base import DataFrameParser, KeyValueParser


class TSVDataFrameParser(DataFrameParser):
    """Parser for TSV to pandas ``DataFrame``"""

    @property
    def delimiter(self) -> str:
        r""":return: ``'\t'``"""
        return '\t'


class TSVKeyValueParser(KeyValueParser):
    """Key-value parser with tabs as a delimiter"""

    @property
    def delimiter(self) -> str:
        r""":return: ``'\t'``"""
        return '\t'
