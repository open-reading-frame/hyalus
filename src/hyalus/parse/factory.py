"""Functionality for generating ResultsParser instances from file paths"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
from typing import Type, TypeAlias

from hyalus.parse.base import ResultsParser
from hyalus.parse.json import JSONParser

ParserMap: TypeAlias = dict[str, Type[ResultsParser]]

#: Controls the ResultsParser class that is associated with specific file names - takes priority over extension
_name_map: ParserMap = {}

#: Controls the ResultsParser class that is associated with certain extensions
_ext_map: ParserMap = {".json": JSONParser}

try:
    from hyalus.parse import csv, tsv

    _ext_map[".csv"] = csv.CSVDataFrameParser
    _ext_map[".tsv"] = tsv.TSVDataFrameParser
except ImportError:
    _ext_map[".csv"] = csv.CSVKeyValueParser
    _ext_map[".tsv"] = tsv.TSVKeyValueParser

try:
    from hyalus.parse.h5 import H5Parser

    _ext_map[".h5"] = H5Parser
except ImportError:
    pass


# pylint: disable=dangerous-default-value
def get_parser(
    path: str | Path, name_map: ParserMap = _name_map, ext_map: ParserMap = _ext_map
) -> ResultsParser | None:
    """Based on a given path's filename/extension, determine which applicable ResultsParser, if any, should parse it and
    create an instance of that parser

    :param path: The path corresponding to the file to parse
    :param name_map: The mapping of file name to ResultsParser class to use, defaulting to :py:obj:`_name_map`
    :param ext_map: The mapping of file extension to ResultsParser class to use, defaulting to :py:obj:`_ext_map`
    :return: The instantiated ResultsParser or None if no corresponding parser could be found
    """
    path = Path(path)

    # Direct name match
    if path.name in name_map:
        return name_map[path.name](path)

    # Handle wildcard matches
    for ext, parser in ext_map.items():
        if path.suffix == ext:
            return parser(path, use_glob=True)

    return None
