"""Tags representing different styles of testing"""
# pylint: disable=too-few-public-methods

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.config.tags.base import TagBase, TagType


class TestTypeTag(TagBase):
    """Base class for tags describing the type of testing being performed"""

    # This is not a class for unit testing, set __test__ to False so pytest ignores it
    __test__ = False

    @property
    def _types(self) -> TagType:
        return TagType.TEST_TYPE


class UnitTest(TestTypeTag):
    """Tag to denote a test as a unit test"""


class FunctionalTest(TestTypeTag):
    """Tag to denote a test as a functional test"""


class IntegrationTest(TestTypeTag):
    """Tag to denote a test as an integration test"""


class EndToEndTest(TestTypeTag):
    """Tag to denote a test as an end-to-end style test"""


class SmokeTest(TestTypeTag):
    """Tag to denote a test as a smoke test"""


class PerformanceTest(TestTypeTag):
    """Tag to denote a test as a performance test"""


class RegressionTest(TestTypeTag):
    """Tag to denote a test as a regression test"""

    def __init__(self, info: str) -> None:
        """Ctor.

        :param info: Information detailing why this regression test exists
        """
        super().__init__(info=info)
