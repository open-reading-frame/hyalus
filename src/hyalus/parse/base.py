"""Base logic for output results parsing"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import abc
import csv
from pathlib import Path
from typing import Any, TypeAlias
from typing_extensions import Unpack

try:
    import pandas as pd
except ImportError:
    pd = None

from hyalus.utils.file_utils import glob_file
from hyalus.utils.pandas_utils import subset_dataframe
from hyalus.utils.typing_utils import type_string

# TypeAliases for search inputs for ResultsParsers
# Unpack must be used for backwards compatibility with Python 3.10
# mypy is still working on fully supporting variadic generics introduced in PEP 646
# TODO: When https://github.com/python/mypy/issues/12280 has been addressed, remove any type: ignore comments

# Non-empty tuple in which elements can be of any type
SearchParams: TypeAlias = tuple[Any, Unpack[tuple[Any, ...]]]  # type: ignore

# Non-empty tuple in which elements must be 2-element tuples with a string as the first element and any as the second
DFSearchParams: TypeAlias = tuple[tuple[str, Any], Unpack[tuple[tuple[str, Any], ...]]]  # type: ignore

# Single-element tuple with a string as its element
KVSearchParams: TypeAlias = tuple[str]


class ResultsParser(abc.ABC):
    """Base class for output results parsing"""

    def __init__(self, file_path: str | Path, use_glob: bool = False, cache: bool = True, **kwargs: Any) -> None:
        """Ctor.

        :param file_path: Path to results file to parse. Should include directory and file name/wildcard
        :param use_glob: If True will treat the given path as a wildcard. If false will treat as a path and file name.
        :param cache: Boolean flag defining whether parsed results should be stored in memory or not
        :param kwargs: Any keyword arguments to use in the _parse method
        """
        self.file_path = glob_file(file_path) if use_glob else Path(file_path)
        self.cache = cache
        self.kwargs = kwargs

        self.__parsed_file = None

    def __eq__(self, other):
        # If we are pointing to the same file, then short circuit to True
        if self.file_path == other.file_path:
            return True

        # Otherwise, default to whatever __eq__ method the parsed files have
        return self.parse() == other.parse()

    @abc.abstractmethod
    def _parse(self) -> Any:
        """Private parsing method for the given file

        :return: The file parsed into memory. Classes defining this method should define the output data structure.
        """

    def parse(self) -> Any:
        """Parse the given file into a workable data format in memory

        :return: The file parsed into memory
        """
        if self.cache:
            if self.__parsed_file is None:
                self.__parsed_file = self._parse()

            return self.__parsed_file

        return self._parse()

    @abc.abstractmethod
    def _search(self, parsed_file: Any, to_search: SearchParams) -> Any:
        """Private searching method to locate the given value

        :param parsed_file: The parsed file to search
        :param to_search: The keys/indices/row/column/etc. to find within the given file
        :return: The retrieved value
        """

    def search(self, to_search: Any) -> Any:
        """Retrieve a value from the parsed file based on given search fields

        :param to_search: The keys/indices/row/column/etc. to use to  the given file
        :return: The retrieved value, if Any
        """
        parsed_file = self.parse() if self.__parsed_file is None else self.__parsed_file

        # _search methods expect non-empty tuples. Convert lists to a tuple, otherwise assume a single key/index/etc.
        # was given, and wrap it as a single-element tuple for processing
        if isinstance(to_search, list):
            to_search = tuple(to_search)
        else:
            to_search = (to_search,)

        return self._search(parsed_file, to_search)


class DataFrameParser(ResultsParser):
    """Base class for ``DataFrame`` parsers"""

    def __eq__(self, other):
        # Override default __eq__ because of how DataFrame equality is handled
        if self.file_path == other.file_path:
            return True

        return self.parse().equals(other.parse())

    @property
    @abc.abstractmethod
    def delimiter(self) -> str:
        """:return: The delimiter for the given DataFrame parser"""

    def _parse(self) -> pd.DataFrame:
        """Parse the given file into a pandas ``DataFrame``, passing any given kwargs into ``pd.read_csv``

        :return: The instantiated pandas ``DataFrame``
        """
        return pd.read_csv(self.file_path, sep=self.delimiter, **self.kwargs)

    def _search(self, parsed_file: pd.DataFrame, to_search: DFSearchParams) -> pd.DataFrame:
        """Subset the given DataFrame to records matching the given (column, value) pairs

        :param parsed_file: The pandas DataFrame to subset
        :param to_search: Tuples of (column, value) that records must match
        :return: The DataFrame, subset down to entries matching the given list of tuples
        """
        return subset_dataframe(parsed_file, to_search)


class KeyValueParser(ResultsParser):
    """Base class for key-value parsers"""

    @property
    @abc.abstractmethod
    def delimiter(self) -> str:
        """:return: The delimiter for the given key-value parser"""

    def _parse(self) -> dict[str, Any]:
        """Convert the given file of key-value pairs into a dictionary

        :return: The dictionary of parsed key-value pairs
        """
        parsed = {}

        with open(self.file_path, 'r', encoding="utf-8", newline="") as fh:
            dialect = csv.Sniffer().sniff(fh.read(1024), delimiters=self.delimiter)
            fh.seek(0)
            reader = csv.reader(fh, dialect=dialect, delimiter=self.delimiter)

            for line in reader:
                parsed[line[0]] = type_string(self.delimiter.join(line[1:]))

        return parsed

    def _search(self, parsed_file: dict[str, Any], to_search: KVSearchParams) -> Any:  # type: ignore
        """Search the parsed file for an entry with the given key to_find

        :param parsed_file: The dict of parsed key/value pairs
        :param to_find: The key to find
        :return: The value for the given key, if found
        """
        return parsed_file[to_search[0]]
