"""Functionality for updating settings for running hyalus"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import json
from pathlib import Path
import re
from typing import Any, Iterable, Pattern, Sequence, TypeAlias
from types import GenericAlias

from hyalus.utils.json_utils import JSONLiteral
from hyalus.utils.typing_utils import type_check

# Settings can be stored as int, float, str, bool, None, or a Sequence of those values
SettingValue: TypeAlias = JSONLiteral | Sequence[JSONLiteral]


class InvalidSetting(Exception):
    """To be raised when trying to update a setting with an invalid value, or the setting does not exist"""


# pylint: disable=too-few-public-methods
class HyalusSetting:
    """Container class to store hyalus setting attributes"""

    def __init__(self, name: str, description: str, allowable_values: type | Iterable | Pattern, default: Any):
        """Ctor.

        :param name: The name of the setting
        :param description: Description of the setting
        :param allowable_values: Type of allowable values, or Iterable of specific allowed values
        :param default: The default for the setting
        """
        self.name = name
        self.description = description
        self.allowable_values = allowable_values
        self.default = default

        # Will fail when this module is imported if the default is invalid - acts as an implementation check
        assert self.value_is_valid(self.default)

    def __str__(self) -> str:
        if isinstance(self.allowable_values, type):
            type_str = self.allowable_values.__name__
        elif isinstance(self.allowable_values, Pattern):
            type_str = self.allowable_values.pattern
        else:
            type_str = str(self.allowable_values)

        default_str = f"'{self.default}'" if isinstance(self.default, str) else self.default

        return f"{self.name} (allowable values - {type_str}, default {default_str}): {self.description}"

    def value_is_valid(self, value: Any) -> bool:
        """Checks if the given value is allowed based on self.allowable_values

        :param value: The value to check
        :return: True if the value is allowed else False
        """
        if isinstance(self.allowable_values, type | GenericAlias):
            return type_check(value, self.allowable_values)

        if isinstance(self.allowable_values, Pattern):
            return re.match(self.allowable_values, str(value)) is not None

        return value in self.allowable_values


DEBUG = HyalusSetting(
    "debug",
    "Debug mode for hyalus - turns on debug logging, test runs will always be kept. Overrides cleanup_on_pass",
    bool,
    False,
)

STDOUT = HyalusSetting(
    "stdout",
    "Log test run messages to stdout",
    bool,
    False,
)


CONFIG_AUTHOR = HyalusSetting(
    "config_author",
    "Name of author field for the template command. Also used for the credits field",
    str,
    "",
)

TEMPLATE_OUTPUT_DIR = HyalusSetting(
    "template_output_dir",
    "Path to the output directory when running the template command. Note if given a relative path, it will be "
    "relative to where hyalus is run from",
    str,
    '.',
)

RUNS_DIR = HyalusSetting(
    "runs_dir",
    "Directory to output test runs to. Note if given a relative path, it will be relative to where hyalus is run from",
    str,
    '.',
)

SEARCH_DIRS = HyalusSetting(
    "search_dirs",
    "Comma-delimited list of directories to search for hyalus tests in. Note if given a relative path, it will be "
    "relative to where hyalus is run from",
    list[str],
    ['.'],
)

CLEANUP_ON_PASS = HyalusSetting(
    "cleanup_on_pass",
    "Cleanup passing test runs",
    bool,
    False,
)

TAG_OPERATOR = HyalusSetting(
    "tag_operator",
    "Operator to use when searching for tests matching given tags when using the runsuite command",
    ["all", "any"],
    "any",
)

OLDEST_TEST_RUN = HyalusSetting(
    "oldest_test_run",
    "Either the oldest date or the number of days from today for a test run to be kept when using hyalus clean",
    re.compile(r"^\d{4}-\d{2}-\d{2}|\d+$"),
    "0001-01-01",
)

NEWEST_TEST_RUN = HyalusSetting(
    "newest_test_run",
    "The newest date for a test run to be kept when using hyalus clean",
    re.compile(r"^\d{4}-\d{2}-\d{2}|\d+$"),
    "9999-12-31",
)

FORCE_CLEAN = HyalusSetting(
    "force_clean",
    "Flag to indicate that rest runs should be removed without confirmation when using hyalus clean",
    bool,
    False,
)


HYALUS_SETTINGS: dict[str, HyalusSetting] = {
    DEBUG.name: DEBUG,
    STDOUT.name: STDOUT,
    CONFIG_AUTHOR.name: CONFIG_AUTHOR,
    TEMPLATE_OUTPUT_DIR.name: TEMPLATE_OUTPUT_DIR,
    RUNS_DIR.name: RUNS_DIR,
    SEARCH_DIRS.name: SEARCH_DIRS,
    CLEANUP_ON_PASS.name: CLEANUP_ON_PASS,
    TAG_OPERATOR.name: TAG_OPERATOR,
    OLDEST_TEST_RUN.name: OLDEST_TEST_RUN,
    NEWEST_TEST_RUN.name: NEWEST_TEST_RUN,
    FORCE_CLEAN.name: FORCE_CLEAN,
}


class HyalusSettingsRunner:
    """Orchestrator for reading/writing hyalus settings files"""

    def __init__(
        self,
        settings_file: str | Path,
        output_descriptions: bool = False,
        to_update: dict[str, SettingValue] = None,
        to_reset: Sequence[str] = None,
    ) -> None:
        """Ctor.

        :param settings_files: Path to the settings JSON file to load
        :param output_descriptions: True if setting descriptions should be printed before settings values are
        :param to_update: Mapping of setting name to value that should be updated
        :param to_reset: List of setting names that should be reset to default values
        """
        self.settings_file = Path(settings_file)
        self.output_descriptions = output_descriptions
        self.to_update = to_update if to_update else {}
        self.to_reset = to_reset if to_reset else []

        if intersection := set(self.to_update) & set(self.to_reset):
            raise ValueError(f"Setting(s) {intersection} specified for update and reset. Double check configuration.")

        self.__settings: dict[str, SettingValue] = None

    @property
    def settings(self) -> dict[str, SettingValue]:
        """Parsed settings, name to value mapping. Creates settings file and populates with defaults if none exists

        :return: The parsed settings
        """
        if self.__settings is None:
            self.__settings = self.__update_settings_file()

        return self.__settings

    def __update_settings_file(self) -> dict[str, SettingValue]:
        """Parse settings file and update contents based on any new settings that are missing in the file. If the file
        cannot be parsed, it will be overwritten with a default settings file.

        """
        if not self.settings_file.exists():
            self.settings_file.touch()

        with open(self.settings_file, 'r', encoding="utf-8") as fh:
            try:
                settings = json.load(fh)
            except json.decoder.JSONDecodeError:
                settings = {}

        for name, hyalus_setting in HYALUS_SETTINGS.items():
            if name not in settings:
                settings[name] = hyalus_setting.default

        with open(self.settings_file, 'w', encoding="utf-8") as fh:
            json.dump(settings, fh, indent=4)

        return settings

    def print_descriptions(self) -> None:
        """Print descriptions of each setting to stdout"""
        for setting in HYALUS_SETTINGS.values():
            print(setting)

    def print_settings(self) -> None:
        """Print current settings to stdout"""
        for name, value in self.settings.items():
            print(f"{name}: {value}")

    def update(self) -> None:
        """Update settings in place based on given updates"""
        for name, value in self.to_update.items():
            if name not in HYALUS_SETTINGS:
                raise InvalidSetting(f"{name} is not a valid hyalus setting name")

            if HYALUS_SETTINGS[name].allowable_values == list[str]:
                value = str(value).split(',')
                self.to_update[name] = value

            if not HYALUS_SETTINGS[name].value_is_valid(value):
                if isinstance(HYALUS_SETTINGS[name].allowable_values, type):
                    # For some reason even within this isinstance check, mypy thinks we might be handling an Iterable
                    constraint = HYALUS_SETTINGS[name].allowable_values.__name__  # type: ignore
                else:
                    constraint = str(HYALUS_SETTINGS[name].allowable_values)

                raise InvalidSetting(f"{value} does not meet constraints for setting {name} - expected {constraint}")

        self.settings.update(self.to_update)

        with open(self.settings_file, 'w', encoding="utf-8") as fh:
            json.dump(self.settings, fh, indent=4)

    def reset(self) -> None:
        """Reset specified settings to their defaults"""
        for name in self.to_reset:
            if name not in HYALUS_SETTINGS:
                raise InvalidSetting(f"{name} is not a valid hyalus setting name")

        self.settings.update({name: HYALUS_SETTINGS[name].default for name in self.to_reset})

        with open(self.settings_file, 'w', encoding="utf-8") as fh:
            json.dump(self.settings, fh, indent=4)

    def run(self) -> None:
        """Update settings based on given updates and then print out current settings"""
        self.update()
        self.reset()

        if self.output_descriptions:
            self.print_descriptions()
            print("")

        self.print_settings()
