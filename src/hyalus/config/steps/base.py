"""Base logic for Step classes"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import abc
from enum import IntEnum, unique
import logging
from pathlib import Path
from typing import final, Any, NamedTuple, Type

from hyalus.config.common import HYALUS_PATH, HYALUS_LOG, INPUT_PATH, OUTPUT_PATH, TMP_PATH, STEP_LOG
from hyalus.utils import logging_utils

_logger = logging.getLogger("hyalus.config.steps.base")


@unique
class StepStatus(IntEnum):
    """Possible statuses from running a Step. Exit code convention is the inspiration here."""

    PASS = 0
    ERROR = 1
    FAIL = 3  # Do not use 2 as depending on shell some commands exit with error code 2 when used improperly

    def __bool__(self) -> bool:
        return self.name == "PASS"

    @classmethod
    def _missing_(cls, value: Any) -> "StepStatus":
        """Override default behavior for missing value to always point to ERROR"""
        return cls.ERROR

    @classmethod
    def get_by_bool(cls: Type["StepStatus"], value: bool) -> "StepStatus":
        """Get a StepStatus instance from a boolean value

        :param value: The bool
        :return: PASS if given True, else FAIL
        """
        if value is True:
            return cls.PASS

        return cls.FAIL


class StepOutput(NamedTuple):
    """Tuple containing Step output and PASS/FAIL/ERROR status of the execution"""

    output: Any
    status: StepStatus


class StepError(Exception):
    """Error to be raised when Step execution ends in error"""


# pylint: disable=too-many-instance-attributes
class StepBase(abc.ABC):
    """Base class for Steps"""

    # pylint: disable=attribute-defined-outside-init
    def _load(self, step_number: int, run_dir: str | Path) -> None:
        """Convenience method for hyalus runner to load info needed by each step

        :param step_number: The number of this step based on other steps being run
        :param run_dir: The directory for the current run
        """
        self.step_number: int = step_number
        self.run_dir: Path = Path(run_dir)
        self.step_log: Path = run_dir / HYALUS_PATH / STEP_LOG.format(self.step_number, self.__class__.__name__)

        self.input_dir: Path = run_dir / INPUT_PATH
        self.output_dir: Path = run_dir / OUTPUT_PATH
        self.tmp_dir: Path = run_dir / TMP_PATH
        self.hyalus_dir: Path = run_dir / HYALUS_PATH
        self.hyalus_log: Path = run_dir / HYALUS_LOG

        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}_{self.step_number}")

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def needs(self) -> list[str] | None:
        """File paths or extensions of files needed to run this Step

        :return: The list of file paths or extensions to run the Step, or None if none are needed
        """

    @property
    def halt_on_failure(self) -> bool:
        """Set to True for a given Step if when it fails (different from error) test execution should halt

        :return: True by default, can be overridden by subclasses
        """
        return True

    def get_logger(self, name: str = None) -> logging.Logger:  # pylint: disable=unused-argument
        """Used to override logger retrieval during step execution

        :return: self._logger
        """
        return self._logger

    @final
    def run(self, *args) -> Any:
        """Run the Step from start to finish and capture results

        :return: Output from running the Step
        """
        self._load(*args)

        logging_utils.add_file_handler(self.hyalus_log, self._logger)
        logging_utils.add_file_handler(self.step_log, self._logger)

        # Whenever something in this Step tries to log a message, send it through the Step's logger instead
        old_get_logger = logging.getLogger
        logging.getLogger = self.get_logger

        try:
            pre_process_output = self._pre_process()  # pylint: disable=assignment-from-none
            run_workflow_output = self._run_workflow(pre_process_output)
            return self._post_process(run_workflow_output)
        except Exception as exc:
            self._logger.error(exc)
            raise
        finally:
            logging_utils.remove_file_handler(self.hyalus_log, self._logger)
            logging_utils.remove_file_handler(self.step_log, self._logger)
            logging.getLogger = old_get_logger

    def _pre_process(self) -> Any:
        """Pre-processing for running the Step's workflow

        :return: Output from pre-processing to pass to _run_workflow
        """
        return None

    @abc.abstractmethod
    def _run_workflow(self, pre_process_output: Any = None) -> StepOutput:
        """Run the Step's workflow

        :param pre_process_output: Output from pre-processing
        :return: Output from running the workflow to pass to _post_process
        """

    def _post_process(self, workflow_output: StepOutput = None) -> StepOutput:
        """Post-processing for running the Step's workflow prior to capturing results

        :param workflow_output: Output from running the workflow
        :return: Output from post-processing to return to the caller
        """
        return workflow_output
