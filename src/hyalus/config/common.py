"""Common utilities for use in hyalus configuration parsing, linting, etc."""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from enum import Enum
from pathlib import Path
from typing import Any

INPUT_PATH = Path("input")
OUTPUT_PATH = Path("output")
TMP_PATH = Path("tmp")
HYALUS_PATH = Path("hyalus")
TEST_SUBDIRS = (OUTPUT_PATH, TMP_PATH, HYALUS_PATH)

CONFIG_PY = Path("config.py")
HYALUS_LOG = HYALUS_PATH / "hyalus.log"
RUN_METADATA = HYALUS_PATH / "run_metadata.json"

STEP_LOG = "{}_{}_log.txt"


class ConfigStatus(str, Enum):
    """Different statuses for config file loading"""

    VALID = "Hyalus config file passed all checks"
    NOT_FOUND = "Hyalus config file could not be found"
    COULD_NOT_BE_LOADED = "Hyalus config file could not be loaded - double check imports, syntax, etc."
    MISSING_FIELDS = "Hyalus config file did not have all required fields"
    INVALID_FIELDS = "Hyalus config file had fields that did not pass quality check"
    PYLINT_FAILURE = "Hyalus config file failed pylint check - see config_pylint_output.txt for failures"
    OTHER_FAILURE = "Hyalus config file was found to be invalid for some other reason"


class InvalidHyalusConfig(Exception):
    """To be raised when a config file cannot be parsed, does not have required fields, or is otherwise invalid"""

    def __init__(self, failure: ConfigStatus, *args: Any, additional_info: str = None) -> None:
        msg = failure.value if not additional_info else f"{failure.value}\n\n{additional_info}"
        super().__init__(msg, *args)


class Failure(Exception):
    """Parent class for Exceptions that result in a message logged but do not halt processing"""


class Error(Exception):
    """Parent class for Exceptions that result in both a message logged as well as halting processing"""
