"""H5 file parsers - importing this module will make hyalus attempt to import h5py and numpy"""
# pylint: disable=c-extension-no-member

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from typing import TypeAlias, Any
from typing_extensions import Unpack

# h5py is not typed and there are no plans to type it https://github.com/h5py/h5py/issues/1912
import h5py  # type: ignore
import numpy as np

from hyalus.parse.base import ResultsParser

# Non-empty tuple in which the first element is a string and any following elements can be of any type
# TODO: When https://github.com/python/mypy/issues/12280 has been addressed, remove any type: ignore comments
# pylint: disable=invalid-name
H5SearchParams: TypeAlias = tuple[str, Unpack[tuple[Any, ...]]]  # type: ignore


class Dataset(h5py.Dataset):
    """Dataset that can determine if it is equal to another Dataset or not"""

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, h5py.Dataset):
            return False

        # Indexing a Dataset object returns a numpy array of the data
        # TODO: Probably a smarter, less memory intensive way to do this?
        return np.array_equal(self[:], other[:])

    def __ne__(self, other: Any) -> bool:
        return not self == other


class Group(h5py.Group):
    """Group that can determine if it is equal to another Group or not"""

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, h5py.Group):
            return False

        for key, value in self.items():
            if key not in other:
                return False

            if value != other[key]:
                return False

        return True

    def __ne__(self, other: Any) -> bool:
        return not self == other

    @h5py._objects.with_phil
    def __getitem__(self, name):  # pragma: no cover
        """Copied more or less directly from https://github.com/h5py/h5py/blob/3.8.0/h5py/_hl/group.py#L349"""
        if isinstance(name, h5py.h5r.Reference):
            oid = h5py.h5r.dereference(name, self.id)
            if oid is None:
                raise ValueError("Invalid HDF5 object reference")
        elif isinstance(name, (bytes, str)):
            oid = h5py.h5o.open(self.id, self._e(name), lapl=self._lapl)
        else:
            raise TypeError(f"Accessing a group is done with bytes or str, not {type(name)}")

        match h5py.h5i.get_type(oid):
            case h5py.h5i.GROUP:
                return Group(oid)
            case h5py.h5i.DATASET:
                return Dataset(oid, readonly=self.file.mode == 'r')
            case h5py.h5i.DATATYPE:
                return h5py.Datatype(oid)
            case _:
                raise TypeError("Unknown object type")


class File(Group, h5py.File):
    """Inherit the Group __eq__/__getitem__ methods and everything else from h5py.File"""


class H5Parser(ResultsParser):
    """Parser for HDF5 files"""

    def _parse(self) -> File:
        """Private parsing method for the given file

        :return: The HDF5 file parsed into memory
        """
        return File(self.file_path, 'r')

    def _search(self, parsed_file: File, to_search: H5SearchParams) -> Any:
        """Searches the given HDF5 file based on the list of groups/datasets/indices

        :param parsed_file: The H5 file to search
        :param to_search: The list of groups/datasets/indices to use to index into the H5 file
        :return: The retrieved value
        """
        search_result = None

        for accesor in to_search:
            if search_result is None:
                search_result = parsed_file[accesor]
            else:
                search_result = search_result[accesor]

        return search_result
