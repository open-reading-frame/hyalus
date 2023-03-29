"""Functionality to tag certain tests with metadata like expected runtime, project, etc."""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import abc
from enum import Enum
from functools import total_ordering


@total_ordering
class TagType(str, Enum):
    """High-level types of Tags"""

    RUNTIME = "Runtime"
    TEST_TYPE = "Test Type"
    ANALYSIS = "Analysis"
    MISC = "Misc"

    def __lt__(self, other):
        return self.value < other.value


class TagBase(abc.ABC):
    """Base class for tags"""

    def __init__(self, info: str = ""):
        """Ctor.

        :param info: Any info to store with a Tag, on a per-tag basis
        """
        self.info = info

    def __str__(self) -> str:
        return self.__class__.__name__ + f": {self.info}" if self.info else ""

    def __eq__(self, other) -> bool:
        """Equality defined as being instances of the same class"""
        return self.__class__ is other.__class__

    def __hash__(self) -> int:
        return hash(f"{self.__class__.__name__}_{self.info}")

    @property
    @abc.abstractmethod
    def _types(self) -> TagType | set[TagType]:
        """:return: The "types" of this Tag, e.g. speed descriptor, type of test, etc."""

    @property
    def types(self) -> set[TagType]:
        """:return: The "types" of this Tag, e.g. speed descriptor, type of test, etc."""
        tag_types = set()

        if isinstance(self._types, TagType):
            tag_types.add(self._types)
        else:
            for tag_type in self._types:
                tag_types.add(tag_type)

        return tag_types
