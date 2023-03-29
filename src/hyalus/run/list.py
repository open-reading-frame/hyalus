"""Functionality for finding hyalus tests and listing them out"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
from typing import Callable, Sequence

from hyalus.run.common import find_all_tests, find_tests_by_tag


# pylint: disable=too-few-public-methods
class HyalusListRunner:
    """Class that finds and outputs test names based on tags"""

    def __init__(
        self, search_dirs: Sequence[str | Path] = None, tags: Sequence[str] = None, tag_op: Callable[..., bool] = all
    ) -> None:
        """Ctor.

        :param search_dirs: The directories to search for tests, defaults to cwd
        :param tags: List of tags to find
        :param tag_op: Operator to apply to tag matching - ``all`` if test must have all given tags, ``any`` if the test
            must have any of the given tags
        """
        self.search_dirs = [Path(search_dir) for search_dir in search_dirs] if search_dirs else [Path('.')]
        self.tags = tags if tags else []
        self.tag_op = tag_op

        # Print all tests if no tag filters given
        self.print_all: bool = not bool(tags)

    def run(self) -> None:
        """Find relevant tests and print them to stdout"""
        if self.print_all:
            test_paths = find_all_tests(self.search_dirs)
        else:
            test_paths = find_tests_by_tag(self.tags, self.tag_op, self.search_dirs)

        for test in sorted({test_path.name for test_path in test_paths}):
            print(test)
