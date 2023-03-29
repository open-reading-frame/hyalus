"""Hyalus test run cleanup"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import date, MINYEAR, MAXYEAR
from pathlib import Path
import shutil
from typing import Sequence, Callable

from hyalus.run.common import HyalusRun, find_relevant_test_runs


# pylint: disable=too-many-arguments
class HyalusCleanRunner:
    """Orchestration for hyalus test run cleanup"""

    def __init__(
        self,
        runs_dir: str | Path,
        to_clean: Sequence[str] = None,
        tags: Sequence[str] = None,
        tag_op: Callable[..., bool] = all,
        oldest: date = None,
        newest: date = None,
        force: bool = False,
    ) -> None:
        """Ctor.

        :param runs_dir: The runs directory to clean up
        :param to_clean: List of test names/test plans corresponding to tests to clean up. If none given, ALL test runs
            will be fair game
        :param tags: Tags that when matched will mark a test for removal. If none given, ALL given tests will be removed
        :param tag_op: Operator to apply to tag matching - ``all`` if test must have all given tags, ``any`` if the test
            must have any of the given tags
        :param oldest: Date string in format ``YYYY-MM-DD`` marking the oldest date a test can have and be kept. Any
            tests older than this date will be removed. If none given, the earliest possible date is used.
        :param newest: Date string in format ``YYYY-MM-DD`` marking the newest date a test can have and be kept. Any
            tests newer than this date will be removed. If none given, the newest/latest possible date is used.
        :param force: If set to True, will force remove test runs matching criteria. If set to False, will prompt user
            confirmation prior to actual removal of tests
        """
        self.runs_dir = Path(runs_dir)
        self.to_clean = to_clean if to_clean else []
        self.tags = tags if tags else []
        self.tag_op = tag_op
        self.oldest = oldest if oldest else date(MINYEAR, 1, 1)
        self.newest = newest if newest else date(MAXYEAR, 12, 31)
        self.force = force

    def confirm_test_run_removal(self, test_runs: Sequence[HyalusRun]) -> bool:
        """Ask the user to confirm given test runs for removal

        :param test_runs: The test runs marked for removal
        :return bool: True if the user confirmed the test removal, or if self.force is True, else False
        """
        if self.force:
            return True

        remove_tests = input(f"{len(test_runs)} test runs marked for removal. Are you sure you want to proceed? Y/N\n")

        return remove_tests.lower() in {"y", "yes"}

    def run(self) -> None:
        """Find relevant test runs to remove, confirm with the user that it's ok, and then remove them"""
        test_runs = list(
            find_relevant_test_runs(
                self.runs_dir,
                test_names=self.to_clean,
                match_tags=self.tags,
                tag_op=self.tag_op,
                oldest=self.oldest,
                newest=self.newest,
            )
        )

        if not test_runs:
            print(f"Couldn't find any test runs to remove in {self.runs_dir} based on given criteria")
            return

        if self.confirm_test_run_removal(test_runs):
            for test_run in test_runs:
                shutil.rmtree(test_run)
            print(f"{len(test_runs)} old test runs have been removed")
        else:
            print("Test run removal canceled")
