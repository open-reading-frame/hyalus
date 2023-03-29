"""Hyalus test running via configuration file input"""
# pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-arguments

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import datetime
import logging
import os
from pathlib import Path
import random
import shutil
import string
from typing import Sequence, Literal

from hyalus.config.common import HYALUS_LOG, InvalidHyalusConfig
from hyalus.config.loader import ConfigLoader
from hyalus.config.steps.base import StepStatus
from hyalus.run.common import DATE_FMT, RUN_DIR_DELIM, HyalusTest, HyalusRun, make_run_dir, find_fs_obj, cwd_reset
from hyalus.utils import logging_utils


class HyalusTestRunner:
    """Config parsing and Step running orchestrator"""

    def __init__(
        self,
        to_run: str | Path,
        runs_dir: str | Path = None,
        search_dirs: Sequence[str | Path] = None,
        cleanup_on_pass: bool = False,
        stdout: bool = False,
        debug: bool = False,
    ) -> None:
        """Ctor.

        :param to_run: The name or path of the test to run - a direct path can be used to prevent Hyalus from failing
            when it finds multiple tests with the same name in the given search_dirs
        :param runs_dir: The directory to output test results to
        :param search_dirs: List of directories containing to be searched for tests
        :param cleanup_on_pass: Flag to remove test run directory if the test passes, default False
        """
        self.to_run = Path(to_run)
        self.runs_dir = Path(runs_dir).absolute() if runs_dir else Path.cwd()
        self.search_dirs = [Path(search_dir).absolute() for search_dir in search_dirs] if search_dirs else [Path.cwd()]
        self.cleanup_on_pass = cleanup_on_pass
        self.stdout = stdout
        self.debug = debug

        self._logger: logging.Logger = None
        self.__test: HyalusTest = None

    @property
    def test(self) -> HyalusTest:
        """Caching of test path based on the value given for the test to run

        :return: The absolute path to the test to run
        """
        if self.__test is None:
            self.__test = HyalusTest(find_fs_obj(self.to_run, self.search_dirs))

        return self.__test

    def _make_run_dir(self, test_path: Path | str, alphanumeric_chars: int = 8) -> HyalusRun:
        """Create a run directory for the test run in the location specified according to the name of the test. Copies
        over all files from the test config directory to the run directory

        :param test_path: Absolute path to the test config directory for the test being run
        :param alphanumeric_chars: The number of alphanumeric characters to add to the directory name
        :return: The Path of the created run directory
        """
        today = datetime.today().strftime(DATE_FMT)
        random_alphanumeric = "".join(random.choices(string.ascii_letters + string.digits, k=alphanumeric_chars))

        run_dir = self.runs_dir / f"{self.to_run.name}{RUN_DIR_DELIM}{today}{RUN_DIR_DELIM}{random_alphanumeric}"

        if run_dir.exists():
            return self._make_run_dir(test_path, alphanumeric_chars=alphanumeric_chars + 1)

        shutil.copytree(test_path, run_dir)

        return make_run_dir(run_dir)

    def test_success(self, run_dir: Path) -> Literal[True]:
        """Note test success via print/log messages, clean up logging and optionally run dir

        :param run_dir: The run directory
        :return: ``True``
        """
        if not self.stdout:
            print(f"{run_dir}: SUCCESS")

        self._logger.info(f"{run_dir}: SUCCESS")

        logging_utils.remove_file_handler(run_dir / HYALUS_LOG, logger=self._logger)

        if self.cleanup_on_pass:
            shutil.rmtree(run_dir)

        return True

    def test_failure(self, run_dir: Path) -> Literal[False]:
        """Note test failure via print/log messages and clean up logging

        :param run_dir: The run directory
        :return: ``False``
        """
        if not self.stdout:
            print(f"{run_dir}: FAILURE")

        self._logger.error(f"{run_dir}: FAILURE")

        logging_utils.remove_file_handler(run_dir / HYALUS_LOG, logger=self._logger)

        return False

    def test_error(self, run_dir: Path, msg: str) -> Literal[False]:
        """Note test error via print/log messages and clean up logging

        :param run_dir: The run directory
        :return: ``False``
        """
        if not self.stdout:
            print(f"{run_dir}: ERROR")
            print(msg)

        self._logger.error(f"{run_dir}: ERROR")
        self._logger.error(msg)

        logging_utils.remove_file_handler(run_dir / HYALUS_LOG, logger=self._logger)

        return False

    @cwd_reset
    def run(self) -> bool:
        """Create the test run directory and then run the test

        :return: True/False based on whether the test passed or not
        """
        logging_utils.configure_logging(log_stdout=self.stdout, debug=self.debug)

        self._logger = logging.getLogger(f"hyalus.run.runtest.{self.to_run}")

        if not self.test.is_valid:
            self._logger.disabled = True
            return self.test_error(self.to_run, "Test does not exist, is a previous run, or is missing config.py")

        run_dir = self._make_run_dir(self.test)
        run_dir.write_run_metadata()

        os.chdir(run_dir)

        logging_utils.add_file_handler(run_dir / HYALUS_LOG, logger=self._logger)

        self._logger.info(f"Running {self.test}")

        try:
            config = ConfigLoader(run_dir.config).run()
        except InvalidHyalusConfig:
            return self.test_error(run_dir, "Config file could not be loaded")

        step_results = []

        for i, step in enumerate(config.STEPS, start=1):
            # Here we are checking for a step error - if it failed to finish, bail after logging which step it was
            try:
                step_output = step.run(i, run_dir)
            except:  # pylint: disable=bare-except
                return self.test_error(run_dir, f"Step {i} {step} ({i}/{len(config.STEPS)})")

            step_results.append(step_output.status)

            if step_output.status is StepStatus.ERROR:
                return self.test_error(run_dir, f"Step {i} {step} ({i}/{len(config.STEPS)})")

            if step_output.status is StepStatus.FAIL and step.halt_on_failure:
                self._logger.error(f"Step {step} ({i}/{len(config.STEPS)}) failed - stopping test execution")
                break

        if all(step_results):
            return self.test_success(run_dir)

        return self.test_failure(run_dir)
