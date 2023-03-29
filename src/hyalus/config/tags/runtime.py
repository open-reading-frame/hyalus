"""Tags associated with runtime"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import abc
from math import inf

from hyalus.config.tags.base import TagBase, TagType


class RuntimeTag(TagBase):
    """Type of Tag that defines the expected runtime of the test"""

    def __str__(self) -> str:
        return self.__class__.__name__ + f": {self.expected_range[0]}-{self.expected_range[1]} minutes"

    @property
    def _types(self) -> TagType:
        return TagType.RUNTIME

    @property
    @abc.abstractmethod
    def expected_range(self) -> tuple[float, float]:
        """:return: The expected range of time, in minutes, for the test to run in"""


class Short(RuntimeTag):
    """Tag for tests that run in under 5 minutes"""

    @property
    def expected_range(self) -> tuple[float, float]:
        """:return: 0-5 minutes"""
        return (0, 5)


class Medium(RuntimeTag):
    """Tag for tests that run in between 5 and 30 minutes"""

    @property
    def expected_range(self) -> tuple[float, float]:
        """:return: 5-60 minutes"""
        return (5, 60)


class Long(RuntimeTag):
    """Tag for tests that run in between 1 and 3 hours"""

    @property
    def expected_range(self) -> tuple[float, float]:
        """:return: 60-180 minutes"""
        return (60, 180)


class ExtraLong(RuntimeTag):
    """Tag for tests that run in between 3 and 24 hours"""

    @property
    def expected_range(self) -> tuple[float, float]:
        """:return: 180-1440 minutes"""
        return (180, 1440)


class AbsoluteUnit(RuntimeTag):
    """Tag for tests that run in more than 24 hours"""

    def __str__(self) -> str:
        return self.__class__.__name__ + f": > {self.expected_range[0]} minutes"

    @property
    def expected_range(self) -> tuple[float, float]:
        """:return: > 1440 minutes"""
        return (1440, inf)
