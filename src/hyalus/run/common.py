"""Common functionality for running hyalus-style tests"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import date, datetime, MINYEAR, MAXYEAR
from functools import wraps
import json
import os
from pathlib import Path
from typing import Callable, Any, Sequence

from hyalus import HYALUS_METADATA
import hyalus.config.common as config_common
from hyalus.config.loader import ConfigLoader

SUITE_EXT = ".ste"
DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M:%S"
RUN_DIR_DELIM = "_"


class Duplicate(Exception):
    """To be raised when more than one filesystem object with the given name is found"""


class NotFound(Exception):
    """To be raised when a given filesystem object cannot be found"""


class InvalidTestSuite(Exception):
    """To be raised when given a test suite that is invalid"""


# Subclass WindowsPath / PosixPath based on whatever Path determines the OS to be
class HyalusTest(Path().__class__):  # type: ignore
    """Class representing a hyalus test Path"""

    @property
    def input_dir(self) -> Path:
        """:return: Path to input subdirectory - not required!"""
        return Path(self) / config_common.INPUT_PATH

    @property
    def config(self) -> Path:
        """:return: Path to config.py"""
        return Path(self) / config_common.CONFIG_PY

    @property
    def is_valid(self) -> bool:
        """Is this a valid hyalus test? Defined as config.py existing and not being a previous test run

        :return: True if valid, else False
        """
        return self.config.exists() and not HyalusRun(self).is_valid

    def matches_tags(self, match_tags: Sequence[str], tag_op: Callable[[Sequence], bool]) -> bool:
        """Does this test match the given tags and tag operator?

        :param match_tags: The tags to match
        :param tag_op: The operator to apply to resulting matches (any, all)
        :return: True if the test matches the given tags, else False
        """
        try:
            config_tags = [tag.__class__.__name__.lower() for tag in ConfigLoader(self.config).run().TAGS]
        except config_common.InvalidHyalusConfig:
            return False

        if not match_tags:
            return True

        return tag_op([match_tag.lower() in config_tags for match_tag in match_tags])


class HyalusRun(HyalusTest):
    """Utility class representing a hyalus test run"""

    # Using __new__ instead of __init__ here since none of the Path classes override __init__
    def __new__(cls, *args, **kwargs) -> "HyalusRun":
        self = cls._from_parts(args)

        self.__test_name: str = None  # type: ignore
        self.__test_date: date = None  # type: ignore
        self.__randomer: str = None  # type: ignore

        return self

    @property
    def hyalus_dir(self) -> Path:
        """:return: Path to hyalus subdirectory"""
        return Path(self) / config_common.HYALUS_PATH

    @property
    def hyalus_log(self) -> Path:
        """:return: Path to hyalus/hyalus.log file"""
        return Path(self) / config_common.HYALUS_LOG

    @property
    def run_metadata(self) -> Path:
        """:return: Path to hyalus/run_metadata.json"""
        return Path(self) / config_common.RUN_METADATA

    @property
    def output_dir(self) -> Path:
        """:return: Path to output subdirectory"""
        return Path(self) / config_common.OUTPUT_PATH

    @property
    def tmp_dir(self) -> Path:
        """:return: Path to tmp subdirectory"""
        return Path(self) / config_common.TMP_PATH

    @property
    def subdirectories(self) -> list[Path]:
        """:return: List of subdirectory Paths that will always be present as part of a run"""
        return [self.hyalus_dir, self.output_dir, self.tmp_dir]

    @property
    def expected_fs_objs(self) -> list[Path]:
        """:return: List of file system objects expected to be in the test run directory"""
        return self.subdirectories + [self.config, self.hyalus_log, self.run_metadata]

    @property
    def test_name(self) -> str:
        """:return: The name of the hyalus test run to produce the test run directory"""
        if self.__test_name is None:
            self.set_run_attrs()

        return self.__test_name

    @property
    def test_date(self) -> date:
        """:return: The date the hyalus test was run"""
        if self.__test_date is None:
            self.set_run_attrs()

        return self.__test_date

    @property
    def randomer(self) -> str:
        """:return: The random alphanumeric string appended to the end of the test directory name"""
        if self.__randomer is None:
            self.set_run_attrs()

        return self.__randomer

    @property
    def is_valid(self) -> bool:
        """Is this a valid hyalus test run? Defined as having a name matching expected naming conventions and having
        a config.py and expected run directory subdirectories

        :return: True if valid, else False
        """
        if self.__test_name is None:
            try:
                self.set_run_attrs()
            except ValueError:
                return False

        return all(path.exists() for path in self.expected_fs_objs)

    def set_run_attrs(self) -> None:
        """Parse directory name for test name, test date, and randomer and store as respective attributes

        :raises ValueError: If the directory name is not in valid format for a test run
        """
        remainder, self.__randomer = self.name.rsplit(RUN_DIR_DELIM, maxsplit=1)
        self.__test_name = remainder.rsplit(RUN_DIR_DELIM, maxsplit=1)[0]
        test_date_str = remainder.split(self.__test_name + RUN_DIR_DELIM)[-1]
        self.__test_date = datetime.strptime(test_date_str, DATE_FMT).date()

    def write_run_metadata(self) -> None:
        """Write metadata JSON file containing information specific to the run"""
        with open(HYALUS_METADATA, 'r', encoding="utf-8") as hyalus_metadata_fh:
            run_metadata = json.load(hyalus_metadata_fh)

        run_metadata["run_start"] = datetime.now().strftime(f"{DATE_FMT} {TIME_FMT}")

        with open(self.run_metadata, 'w', encoding="utf-8") as run_metadata_fh:
            json.dump(run_metadata, run_metadata_fh, indent=4, sort_keys=True)

    def within_date_range(self, oldest: date, newest: date) -> bool:
        """Is this test run within the given date range?

        :param oldest: The oldest date the test can have to be within range
        :param newest: The newest date the test can have to be within range
        :return: True if the test run is within the date range, else False
        """
        return oldest <= self.test_date <= newest


def cwd_reset(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator - keep track of working directory at function call time and always reset it after the function executes

    :param fn: The function to decorate
    :return: Wrapper function
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        pre_fn_call_cwd = os.getcwd()

        try:
            return fn(*args, **kwargs)
        finally:
            os.chdir(pre_fn_call_cwd)

    return wrapper


def make_run_dir(outer_dir: str | Path) -> HyalusRun:
    """Given a directory, create output, tmp, and hyalus subdirectories if they do not already exist

    :param outer_dir: The outer-level directory
    :return: The outer-level directory, with subdirectories created
    """
    run_dir = HyalusRun(outer_dir)

    if not run_dir.is_dir():
        run_dir.mkdir()

    for subdir in run_dir.subdirectories:
        if not subdir.is_dir():
            subdir.mkdir()

    return run_dir


def _parse_test_suite(test_suite: str | Path) -> list[str]:
    """Parse a test suite file into corresponding tests/other test suites

    :param test_suite: The path to the test suite to parse
    :return: List of parsed out test suites/tests contained within the given test suite
    """
    try:
        with open(test_suite, 'r', encoding="utf-8") as fh:
            lines = []
            for line in fh:
                line = line.strip('\n')
                if line and not line.startswith('#'):
                    lines.append(line)
    except Exception as exc:
        raise InvalidTestSuite(f"Test suite {test_suite} could not be parsed") from exc

    return lines


def find_fs_obj(to_find: str | Path, search_dirs: list[Path] = None) -> Path:
    """Given a path, attempt to find a match in from the current the given search directories

    :return: The absolute Path to the filesystem object, if a single instance was found
    :raises NotFound: If the given filesystem object could not be found in any of the given search directories
    :raises Duplicate: If the given filesystem object was found more than once in the given search directories
    """
    if search_dirs is None:
        search_dirs = []

    if (cwd := Path.cwd()) not in search_dirs:
        search_dirs.append(cwd)

    fs_objs = []

    for search_dir in search_dirs:
        if (search_path := search_dir / to_find).exists():
            # Only append if we have not already found this exact path - handles to_find being an absolute path
            if search_path not in fs_objs:
                fs_objs.append(search_path)

    if not fs_objs:
        msg = f"Could not find item {to_find} in directories: {', '.join([str(sd) for sd in search_dirs])}"
        raise NotFound(msg)

    if len(fs_objs) > 1:
        msg = f"Found multiple items with name {to_find}: {', '.join([str(fs_obj) for fs_obj in fs_objs])}"
        raise Duplicate(msg)

    return fs_objs[0].absolute()


def find_all_tests(search_dirs: Sequence[Path]) -> set[HyalusTest]:
    """Given a list of directories to search, find all hyalus tests within them. Note this does not check test validity.

    :param search_dirs: The directories to search
    :return: Absolute paths to hyalus tests found
    """
    tests = set()

    for search_dir in search_dirs:
        for test_dir in search_dir.iterdir():
            if (test := HyalusTest(test_dir)).is_valid:
                tests.add(test.absolute())

    return tests


def find_tests_by_name(test_names: Sequence[str | Path], search_dirs: list[Path]) -> set[HyalusTest]:
    """Given a list of test names and/or test suites and search directories, get absolute paths to the tests

    :param test_names: Names of tests/test suites to find/parse
    :param search_dirs: Directories to search for tests/test suites
    :return: Absolute paths to all tests to run, with any found duplicates ignored
    """
    tests = set()

    for test_path in (Path(t) for t in test_names):
        absolute_test_path = find_fs_obj(test_path, search_dirs=search_dirs)

        if (test := HyalusTest(absolute_test_path)).is_valid:
            tests.add(test)

        # ... And that any file that is given is meant to be a test suite[str(tag) for tag in
        if absolute_test_path.is_file():
            if absolute_test_path.suffix != SUITE_EXT:
                raise InvalidTestSuite(f"Given file {test_path} did not conform to test suite naming convention")
            tests |= find_tests_by_name(_parse_test_suite(absolute_test_path), search_dirs)

    return tests


def find_tests_by_tag(
    match_tags: Sequence[str], tag_op: Callable[[Sequence], bool], search_dirs: Sequence[Path]
) -> set[HyalusTest]:
    """Search the given search directories for hyalus tests matching the given tags

    :param match_tags: List of tag names for tests to match
    :param tag_op: Function to apply to the resulting list of bools coming from match checking, e.g. any/all
    :param search_dirs: The directories to search through for hyalus tests
    :return: List of absolute paths corresponding to tests matching the given tags
    """
    if not match_tags:
        return set()

    tests = set()

    for test in find_all_tests(search_dirs):
        if test.matches_tags(match_tags, tag_op):
            tests.add(test.absolute())

    return tests


def find_test_runs(runs_dir: Path, test_names: Sequence[str] = None) -> set[HyalusRun]:
    """Given a runs directory and list of test names, find all corresponding hyalus test runs

    :param runs_dir: The runs directory to search
    :param test_names: Test names to match, if any
    :return: The hyalus test runs in the runs directory
    """
    test_runs = set()

    for path in runs_dir.iterdir():
        test_run = HyalusRun(path)
        if test_run.is_valid:
            if not test_names or test_run.test_name in test_names:
                test_runs.add(test_run)

    return test_runs


# pylint: disable=too-many-arguments
def find_relevant_test_runs(
    runs_dir: Path,
    test_names: Sequence[str] = None,
    match_tags: Sequence[str] = None,
    tag_op: Callable[[Sequence], bool] = all,
    oldest: date = date(MINYEAR, 1, 1),
    newest: date = date(MAXYEAR, 12, 31),
) -> set[HyalusRun]:
    """Find test runs that match given tags and/or a range of dates

    :param runs_dir: The runs directory to search
    :param test_names: The names of any tests/test plans to filter down to. If none given, all tests are let through.
    :param match_tags: The tags to match
    :param tag_op: The operator to apply for tag matching (any, all)
    :param oldest: Oldest allowed date for a test run, defaults to oldest possible date
    :param newest: Newest allowed date for a test run, defaults to oldest possible date
    :return: The test runs matching the given criteria
    """
    if match_tags is None:
        match_tags = []

    test_runs = set()

    for test_run in find_test_runs(runs_dir, test_names=test_names):
        if test_run.matches_tags(match_tags, tag_op) and test_run.within_date_range(oldest, newest):
            test_runs.add(test_run)

    return test_runs
