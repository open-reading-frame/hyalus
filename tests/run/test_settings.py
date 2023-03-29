"""Tests for the hyalus.run.settings module"""
# pylint: disable=protected-access

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import json
import re

import pytest

from hyalus.run import settings


@pytest.fixture(name="tmp_file")
def fixture_tmp_file(tmp_path):
    """Convenience path generation for a file to write to in the dir pointed to by tmp_path"""
    return tmp_path / "tmp_file.txt"


class TestHyalusSetting:
    """Tests for the HyalusSetting class"""

    def test_str_type(self):
        """Test string formatting when allowable_values is a type"""
        setting = settings.HyalusSetting("type", "description", str, "default")

        assert str(setting) == "type (allowable values - str, default 'default'): description"

    def test_str_pattern(self):
        """Test string formatting when allowable_values is a regex pattern"""
        setting = settings.HyalusSetting("pattern", "description", re.compile(r"^\d$"), "3")

        assert str(setting) == "pattern (allowable values - ^\\d$, default '3'): description"

    def test_str_constraint(self):
        """Test string formatting when allowable_values is a list of values to match"""
        setting = settings.HyalusSetting("constraint", "description", ["one", "two"], "one")

        assert str(setting) == "constraint (allowable values - ['one', 'two'], default 'one'): description"

    def test_value_is_valid_true_type(self):
        """Test input values against type constraints that should all pass"""
        assert settings.HyalusSetting("s1", "", str, "").value_is_valid("string")
        assert settings.HyalusSetting("s1", "", list[str], [""]).value_is_valid(["string1", "string2"])

    def test_value_is_valid_true_pattern(self):
        """Test input values against regex pattern constraints that should all pass"""
        assert settings.HyalusSetting("s1", "", re.compile(r"^\d+$"), "3").value_is_valid("700")
        assert settings.HyalusSetting("s1", "", re.compile(r"^\d{2}$"), "11").value_is_valid("22")

    def test_value_is_valid_true_iterable(self):
        """Test input values against iterable constraints that should all pass"""
        assert settings.HyalusSetting("s1", "", [1, 2, 3], 3).value_is_valid(1)
        assert settings.HyalusSetting("s1", "", {1, 2, 3}, 3).value_is_valid(1)

    def test_value_is_valid_false_type(self):
        """Test input values against type constraints that should all fail"""
        assert not settings.HyalusSetting("s1", "", str, "").value_is_valid(3)
        assert not settings.HyalusSetting("s1", "", list[str], [""]).value_is_valid(["string1", 3])

    def test_value_is_valid_false_pattern(self):
        """Test input values against regex pattern constraints that should all fail"""
        assert not settings.HyalusSetting("s1", "", re.compile(r"^\d+$"), "3").value_is_valid("hi")
        assert not settings.HyalusSetting("s1", "", re.compile(r"^\d{2}$"), "11").value_is_valid("2")

    def test_value_is_valid_false_iterable(self):
        """Test input values against iterable constraints that should all fail"""
        assert not settings.HyalusSetting("s1", "", [1, 2, 3], 3).value_is_valid(4)
        assert not settings.HyalusSetting("s1", "", {1, 2, 3}, 3).value_is_valid(0)

    def test_invalid_default(self):
        """Assert that when a setting is given an invalid default, an AssertionError is raised"""
        with pytest.raises(AssertionError):
            settings.HyalusSetting("s1", "", str, 3)


class TestHyalusSettingsRunner:
    """Tests for the HyalusSettingsRunner class"""

    def test_settings_from_empty_file(self, tmp_file):
        """Assert settings file gets parsed correctly when accessing the settings property"""
        runner = settings.HyalusSettingsRunner(tmp_file)

        assert runner.settings == {s.name: s.default for s in settings.HYALUS_SETTINGS.values()}

    def test_settings_from_partially_full_file(self, tmp_file):
        """Test retrieval of settings with a settings file that has some but not all settings in it"""
        with open(tmp_file, 'w', encoding='utf-8') as json_fh:
            json.dump({"runs_dir": "/path", "force_clean": True}, json_fh)

        runner = settings.HyalusSettingsRunner(tmp_file)

        for name, value in runner.settings.items():
            if name == "runs_dir":
                assert value == "/path"
            elif name == "force_clean":
                assert value is True
            else:
                assert value == settings.HYALUS_SETTINGS[name].default

    def test_print_settings(self, tmp_file, capsys):
        """Assert that settings are printed out in expected format and in expected order"""
        runner = settings.HyalusSettingsRunner(tmp_file)

        runner.print_settings()

        for setting, line in zip(settings.HYALUS_SETTINGS.values(), capsys.readouterr().out.split("\n")):
            assert line == f"{setting.name}: {setting.default}"

    def test_update_valid(self, tmp_path, tmp_file):
        """Assert settings are correctly updated based on given updates to make"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_update={"runs_dir": str(tmp_path)})

        runner.update()

        for name, value in runner.settings.items():
            if name == "runs_dir":
                assert value == str(tmp_path)
            else:
                assert value == settings.HYALUS_SETTINGS[name].default

    def test_update_split_str(self, tmp_file):
        """Assert that list[str] type settings are properly handled in update"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_update={"search_dirs": "dir1,dir2,dir3"})

        runner.update()

        assert runner.settings["search_dirs"] == ["dir1", "dir2", "dir3"]

    def test_update_invalid_name(self, tmp_file):
        """Assert that when given a setting to update that is unknown, InvalidSetting is raised"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_update={"not_a_setting": True})

        with pytest.raises(settings.InvalidSetting):
            runner.update()

    def test_update_invalid_value_type(self, tmp_file):
        """Assert when given a setting to update with a new value of an invalid type, InvalidSetting is raised"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_update={"runs_dir": 4})

        with pytest.raises(settings.InvalidSetting):
            runner.update()

    def test_update_invalid_value_constraint(self, tmp_file):
        """Assert when given a setting to update with a new value not matching constraints, InvalidSetting is raised"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_update={"tag_operator": "bad"})

        with pytest.raises(settings.InvalidSetting):
            runner.update()

    def test_reset_valid(self, tmp_file):
        """Test that the given settings, and only those settings, are correctly reset to their defaults"""
        with open(tmp_file, 'w', encoding='utf-8') as json_fh:
            json.dump({"force_clean": True, "stdout": True}, json_fh)

        runner = settings.HyalusSettingsRunner(tmp_file, to_reset=["force_clean"])

        runner.reset()

        for name, value in runner.settings.items():
            if name == "stdout":
                assert value is True
            else:
                assert value == settings.HYALUS_SETTINGS[name].default

    def test_reset_invalid_name(self, tmp_file):
        """Assert that when given a setting to reset that is unknown, InvalidSetting is raised"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_reset=["not_a_setting"])

        with pytest.raises(settings.InvalidSetting):
            runner.reset()

    def test_reset_and_update_conflict(self, tmp_file):
        """Assert that when given a setting to both update and reset, ValueError is raised"""
        with pytest.raises(ValueError):
            settings.HyalusSettingsRunner(tmp_file, to_update={"force_clean": True}, to_reset=["force_clean"])

    def test_run_descriptions_off(self, tmp_file, tmp_path, capsys):
        """Assert that the run method updates settings and then prints current ones out, description printing off"""
        runner = settings.HyalusSettingsRunner(tmp_file, to_update={"runs_dir": str(tmp_path), "tag_operator": "all"})

        runner.run()

        for setting, line in zip(settings.HYALUS_SETTINGS.values(), capsys.readouterr().out.split("\n")):
            if setting.name == "runs_dir":
                assert line == f"runs_dir: {tmp_path}"
            elif setting.name == "tag_operator":
                assert line == "tag_operator: all"
            else:
                assert line == f"{setting.name}: {setting.default}"

    def test_run_descriptions_on(self, tmp_file, tmp_path, capsys):
        """Assert that the run method prints descriptions, updates settings, and then prints current ones out"""
        runner = settings.HyalusSettingsRunner(
            tmp_file, output_descriptions=True, to_update={"runs_dir": str(tmp_path), "tag_operator": "all"}
        )

        runner.run()

        stdout_lines = capsys.readouterr().out.split("\n")

        for setting in settings.HYALUS_SETTINGS.values():
            assert stdout_lines[0] == str(setting)
            stdout_lines = stdout_lines[1:]

        assert stdout_lines[0] == ""
        stdout_lines = stdout_lines[1:]

        for setting, line in zip(settings.HYALUS_SETTINGS.values(), stdout_lines):
            if setting.name == "runs_dir":
                assert line == f"runs_dir: {tmp_path}"
            elif setting.name == "tag_operator":
                assert line == "tag_operator: all"
            else:
                assert line == f"{setting.name}: {setting.default}"
