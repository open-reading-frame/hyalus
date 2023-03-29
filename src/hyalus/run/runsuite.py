"""Collection and running of multiple hyalus tests"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import logging
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, Sequence

from hyalus.run.common import HyalusTest, find_tests_by_name, find_tests_by_tag
from hyalus.run.runtest import HyalusTestRunner

_logger = logging.getLogger("hyalus.run.runsuite")


class NoTestsFound(Exception):
    """To be raised when the combination of inputs does not correspond to any tests to run"""


# pylint: disable=too-many-instance-attributes, too-many-arguments
class HyalusSuiteRunner:
    """Find relevant tests to run and spin off a process for each one"""

    def __init__(
        self,
        to_run: Sequence[str | Path] = None,
        runs_dir: str | Path = None,
        search_dirs: Sequence[str | Path] = None,
        tags: Sequence[str] = None,
        tag_op: Callable[..., bool] = all,
        cleanup_on_pass: bool = False,
        debug: bool = False,
    ) -> None:
        """Ctor.

        :param to_run: The names or paths of the tests to run - direct paths can be used to prevent Hyalus from failing
            when it finds multiple tests with the same name in the given search_dirs
        :param runs_dir: The directory to output test results to
        :param search_dirs: List of directories containing to be searched for tests and test suites
        :param tags: List of tags to search for within tests, running any tests that match
        :param tag_op: Operator to apply to tag matching - ``all`` if test must have all given tags, ``any`` if the test
            must have any of the given tags
        :param cleanup_on_pass: Flag to remove test run directories if the test passes, default False
        :param debug: Debug logging flag
        """
        self.to_run = [Path(item) for item in to_run] if to_run else []
        self.runs_dir = Path(runs_dir) if runs_dir else Path('.')
        self.search_dirs = [Path(search_dir) for search_dir in search_dirs] if search_dirs else [Path('.')]
        self.tags = tags if tags else []
        self.tag_op = tag_op
        self.cleanup_on_pass = cleanup_on_pass
        self.debug = debug

    def _find_tests_by_name(self) -> set[HyalusTest]:
        """Convenience wrapper for hyalus.run.common.find_tests_by_name

        :return: Set of Paths to tests matching given test names or test suites
        """
        return find_tests_by_name(self.to_run, self.search_dirs)

    def _find_tests_by_tag(self) -> set[HyalusTest]:
        """Convenience wrapper for hyalus.run.common.find_tests_by_tag

        :return: Set of Paths to tests matching given tags
        """
        return find_tests_by_tag(self.tags, self.tag_op, self.search_dirs)

    def get_tests(self) -> list[HyalusTest]:
        """Based on inputs, find the relevant tests to run

        :return: List of uniquified Paths to the tests to run
        """
        return list(self._find_tests_by_name() | self._find_tests_by_tag())

    def run(self) -> bool:
        """Find tests to run and spin off a process for each run, aggregating the results of each test

        :return: Pass if all tests passed, False if no tests were found or if one or more tests failed
        """
        tests = self.get_tests()

        if not tests:
            raise NoTestsFound("No tests were run - check test configuration")

        with Pool() as pool:
            results = pool.map(self.run_test, tests)

            pool.close()
            pool.join()

        return all(results)

    def run_test(self, test: HyalusTest) -> bool:
        """Run a single test. The test path is expected to be an absolute path to the test

        :param test: The absolute Path to the test to run
        :return: The result from running the test
        """
        try:
            return HyalusTestRunner(test, self.runs_dir, cleanup_on_pass=self.cleanup_on_pass, debug=self.debug).run()
        except:  # pylint: disable=bare-except
            return False
