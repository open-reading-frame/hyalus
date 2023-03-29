"""JSON file parsers"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import json
from typing import TypeAlias
from typing_extensions import Unpack

from hyalus.parse.base import ResultsParser
from hyalus.utils.json_utils import JSONObject, JSONValue, json_get

# Non-empty tuple in which each element is either a string or an int
JSONSearchParams: TypeAlias = tuple[str | int, Unpack[tuple[str | int, ...]]]  # type: ignore


class JSONParser(ResultsParser):
    """Parser for JSON files"""

    def _parse(self) -> JSONObject:
        """Private parsing method for the given file

        :return: The JSON file parsed into memory
        """
        with open(self.file_path, 'r', encoding="utf-8") as json_fh:
            return json.load(json_fh)

    def _search(self, parsed_file: JSONObject, to_search: JSONSearchParams) -> JSONValue:
        """Searches the given parsed JSON file based on the list of keys/indices given

        :param parsed_file: The parsed JSON file to search
        :param to_find: The list of keys/indices to use to index into the parsed JSON file
        :return: The retrieved value
        """
        return json_get(parsed_file, to_search)
