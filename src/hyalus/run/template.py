"""Functionality for creating bare bones hyalus tests from a standard template"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import datetime
import logging
from pathlib import Path
from typing import Sequence

from hyalus.config.common import INPUT_PATH, OUTPUT_PATH, TMP_PATH, CONFIG_PY
from hyalus.utils.json_utils import JSONLiteral

CONFIG_TEMPLATE = Path(__file__).parent / "static/config_template"

_logger = logging.getLogger("hyalus.run.template")


class NoKeyErrors(dict):
    """Dict subclass that will just return the key instead of raising a KeyError when given a key not in the dict"""

    def __missing__(self, key):
        return key


class HyalusTemplateRunner:
    """Orchestration of creating test directories from a template"""

    def __init__(
        self,
        test_names: Sequence[str],
        output_dir: str | Path = None,
        template: str | Path = None,
        settings: dict[str, JSONLiteral] = None,
    ) -> None:
        """Ctor.

        :param test_names: Names of tests to generate
        :param output_dir: Output directory path to put the test in
        :param template: Config template to use
        :param settings: User settings for populating the template
        """
        self.test_names = test_names
        self.output_dir = Path(output_dir) if output_dir else Path('.')
        self.template = Path(template) if template else CONFIG_TEMPLATE
        self.settings = NoKeyErrors(settings) if settings else NoKeyErrors({})
        self.settings["date"] = datetime.today().strftime("%Y-%m-%d")

    def make_test(self, test_name: str) -> None:
        """Make a single test in the output directory based on config template and settings"""
        test_path = self.output_dir / test_name

        if test_path.exists():
            _logger.error(f"Directory {test_name} already exists in {self.output_dir}")
            return

        test_path.mkdir(parents=True)

        for path in (INPUT_PATH, OUTPUT_PATH, TMP_PATH):
            (test_path / path).mkdir()

        with open(self.template, 'r', encoding="utf-8") as template_fh:
            template_content = template_fh.read()

        with open((test_path / CONFIG_PY), 'w', encoding="utf-8") as config_fh:
            config_fh.write(template_content.format_map(self.settings))

    def run(self) -> None:
        """Run template creation for each test"""
        for test_name in self.test_names:
            self.make_test(test_name)
