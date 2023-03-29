"""Module responsible for loading a user-generated config file for processing"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import importlib.util
from pathlib import Path
import types
from typing import NamedTuple

from hyalus.config.common import ConfigStatus, InvalidHyalusConfig
from hyalus.config.steps.base import StepBase
from hyalus.config.tags.base import TagBase, TagType
from hyalus.utils.typing_utils import type_check


class ConfigAttr(NamedTuple):
    """Class for defining required config attributes in a hyalus test config file"""

    name: str
    description: str
    type: type


DESCRIPTION = ConfigAttr(
    "TEST_DESCRIPTION",
    "Description of the test - What steps are run? What output is expected? Include links to relevant issues",
    str,
)

INPUT_DATA = ConfigAttr(
    "INPUT_DATA",
    "Description of the input data - Where did the data come from? What modifications were made, and for what reason?",
    str,
)

STEPS = ConfigAttr(
    "STEPS",
    "List of Steps to run for the test. Each step should have a description of its specific purpose",
    list[StepBase],
)

TAGS = ConfigAttr(
    "TAGS",
    "List of Tags for the test, used to be able to sort tests into groups, run specific groups, etc.",
    list[TagBase],
)

AUTHOR = ConfigAttr(
    "__author__",
    "The original author of the test",
    str,
)

CREDITS = ConfigAttr(
    "__credits__",
    "Who worked on this test? Who inspired ideas for the test? Should include the __author__",
    list[str],
)

CREATED_ON = ConfigAttr(
    "__created_on__",
    "The date that this test was written",
    str,
)

REQUIRED_FIELDS = {DESCRIPTION, INPUT_DATA, STEPS, TAGS, AUTHOR, CREDITS, CREATED_ON}
REQUIRED_TAGS = {TagType.RUNTIME}


class ConfigLoader:
    """Loads a hyalus config file and asserts that it is valid prior to kicking off a run"""

    def __init__(self, config_path: str | Path) -> None:
        """Ctor.

        :param config_path: Path to the hyalus config file to load
        """
        self.config_path = config_path

        self.module: types.ModuleType = None

    def run(self) -> types.ModuleType:
        """Load the module from the given config path and lint it

        :return: The instantiated module object
        """
        self.load_module()
        self.lint()

        return self.module

    def load_module(self) -> None:
        """Load the hyalus configuration file into a module object for use in running/linting

        NOTE: This function does not load the module into sys.modules - it cannot be imported with an import statement
        """
        if not Path(self.config_path).is_file():
            raise InvalidHyalusConfig(ConfigStatus.NOT_FOUND)

        try:
            # See https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
            spec = importlib.util.spec_from_file_location("config.py", self.config_path)
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
        except Exception as exc:
            raise InvalidHyalusConfig(ConfigStatus.COULD_NOT_BE_LOADED) from exc

    def lint(self) -> None:
        """Runs the different available lint checks"""
        self._field_check()
        self._type_check()
        self._tag_check()

    def _field_check(self) -> None:
        """Asserts that all expected fields exist in the config file

        :raises InvalidHyalusConfig: If any fields are missing
        """
        missing = sorted({field.name for field in REQUIRED_FIELDS if not hasattr(self.module, field.name)})

        if missing:
            raise InvalidHyalusConfig(ConfigStatus.MISSING_FIELDS, additional_info=f"Missing: {', '.join(missing)}")

    def _type_check(self) -> None:
        """Asserts that the given fields have the correct type - works under the assumption that all fields exist

        :raises InvalidHyalusConfig: If any of the fields have a value with an invalid type
        """
        invalid = set()

        for required_field in REQUIRED_FIELDS:
            module_field = getattr(self.module, required_field.name)

            if not type_check(module_field, required_field.type):
                invalid.add(required_field.name)

        if invalid:
            fields = [field for field in REQUIRED_FIELDS if field.name in invalid]
            msg = '\n'.join([f"type({field.name}) != {field.type}" for field in fields])
            raise InvalidHyalusConfig(ConfigStatus.INVALID_FIELDS, additional_info=msg)

    def _tag_check(self) -> None:
        """Asserts that required types of tags are present

        :raises InvalidHyalusConfig: If any required tags are missing
        """
        tag_types = set()

        for tag in self.module.TAGS:
            tag_types |= tag.types

        missing = sorted(REQUIRED_TAGS - tag_types)

        if missing:
            msg = f"Missing tags with type: {', '.join(tag_type.value for tag_type in missing)}"
            raise InvalidHyalusConfig(ConfigStatus.INVALID_FIELDS, additional_info=msg)
