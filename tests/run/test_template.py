"""Tests for the hyalus.run.template module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import datetime
from pathlib import Path

from hyalus.config.common import INPUT_PATH, OUTPUT_PATH, TMP_PATH, CONFIG_PY
from hyalus.run import template

CONFIG_TEMPLATE = Path(__file__).parent / "../../src/hyalus/run/static/config_template"


class TestHyalusTemplateRunner:
    """Tests for the HyalusTemplateRunner class"""

    def test_run_end_to_end(self, tmp_path):
        """Test basic end-to-end test making functionality"""
        test_names = ["test_1", "test_2", "test_3"]
        settings = {"config_author": "A Dog"}

        runner = template.HyalusTemplateRunner(test_names, tmp_path, settings=settings)

        runner.run()

        with open(CONFIG_TEMPLATE, 'r', encoding="utf-8") as template_fh:
            format_map = {"config_author": "A Dog", "date": datetime.today().strftime('%Y-%m-%d')}
            expected = template_fh.read().format(**format_map)

        for test_name in test_names:
            with open(tmp_path / test_name / CONFIG_PY, 'r', encoding="utf-8") as config_fh:
                config_content = config_fh.read()

            assert config_content == expected

            for path in (INPUT_PATH, OUTPUT_PATH, TMP_PATH):
                assert (tmp_path / test_name / path).exists()

    def test_run_setting_not_found(self, tmp_path):
        """Make sure that if a setting isn't found, it is left unformatted as a key"""
        test_names = ["test_1"]
        settings = {}

        runner = template.HyalusTemplateRunner(test_names, tmp_path, settings=settings)

        runner.run()

        with open(CONFIG_TEMPLATE, 'r', encoding="utf-8") as template_fh:
            format_map = template.NoKeyErrors({"date": datetime.today().strftime('%Y-%m-%d')})
            expected = template_fh.read().format_map(format_map)

        with open(tmp_path / "test_1" / CONFIG_PY, 'r', encoding="utf-8") as config_fh:
            config_content = config_fh.read()

        assert config_content == expected

        for path in (INPUT_PATH, OUTPUT_PATH, TMP_PATH):
            assert (tmp_path / "test_1" / path).exists()

    def test_run_test_already_exists(self, tmp_path):
        """Test early return if a test directory already exists when running the template flow"""
        test_names = ["test_1"]
        settings = {"config_author": "A Cat"}

        test_path = tmp_path / "test_1"
        test_path.mkdir()

        runner = template.HyalusTemplateRunner(test_names, tmp_path, settings=settings)

        runner.run()

        # No subdirectories or files should exist since we should have bailed when we saw the directory already existed
        assert len(list(test_path.iterdir())) == 0
