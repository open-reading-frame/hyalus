"""Tests for the hyalus.run.clean module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import date
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest

from hyalus.run import clean
from hyalus.run.common import HyalusRun

# pylint: disable=duplicate-code
OUTER_DIR = Path(__file__).parent
RUNS_DIR = OUTER_DIR / "runs_dir"

TEST_RUN_1 = HyalusRun(RUNS_DIR / "runtest_1_2023-02-09_ey2S4AGY")
TEST_RUN_2 = HyalusRun(RUNS_DIR / "runtest_2_2023-02-10_ndTVVsed")
TEST_RUN_7 = HyalusRun(RUNS_DIR / "runtest_7_2023-02-11_5KUBAvgo")


@pytest.fixture(name="runs_dir")
def fixture_runs_dir(tmp_path):
    """Copy contents of RUNS_DIR to tmp_path and then return it"""
    shutil.copytree(RUNS_DIR, tmp_path, dirs_exist_ok=True)
    return tmp_path


class TestHyalusCleanRunner:
    """Tests for the HyalusCleanRunner class"""

    def test_confirm_test_run_removal_yes(self):
        """Test confirmation of run removal when runs should be removed based on user input"""
        runner = clean.HyalusCleanRunner(RUNS_DIR, force=False)

        for return_value in ["y", "yes"]:
            with patch("builtins.input", return_value=return_value):
                assert runner.confirm_test_run_removal([TEST_RUN_1])

    def test_confirm_test_run_removal_no(self):
        """Test confirmation of run removal when runs should not be removed based on user input"""
        runner = clean.HyalusCleanRunner(RUNS_DIR, force=False)

        for return_value in ["some", "other", "values"]:
            with patch("builtins.input", return_value=return_value):
                assert not runner.confirm_test_run_removal([TEST_RUN_1])

    def test_confirm_test_run_removal_force(self):
        """Test that confirm_test_run_removal always returns True when force=True"""
        runner = clean.HyalusCleanRunner(RUNS_DIR, force=True)

        for return_value in ["yes", "y", "some", "other", "values"]:
            with patch("builtins.input", return_value=return_value):
                assert runner.confirm_test_run_removal([TEST_RUN_1])

    def test_run_no_tests_found(self, capsys, runs_dir):
        """Test path for when no tests are found for removal"""
        runner = clean.HyalusCleanRunner(runs_dir, to_clean=["runtest_99"], force=True)

        expected_fs_objs = len(list(runs_dir.iterdir()))
        expected_msg = f"Couldn't find any test runs to remove in {runs_dir} based on given criteria"

        runner.run()

        assert expected_fs_objs == len(list(runs_dir.iterdir()))
        assert capsys.readouterr().out.strip('\n') == expected_msg

    def test_run_tests_found_1(self, capsys, runs_dir):
        """Test path for when tests are found for removal, case one"""
        runner = clean.HyalusCleanRunner(runs_dir, force=True)

        expected_fs_objs = len(list(runs_dir.iterdir())) - 3
        expected_msg = "3 old test runs have been removed"

        runner.run()

        assert expected_fs_objs == len(list(runs_dir.iterdir()))
        assert capsys.readouterr().out.strip('\n') == expected_msg

    def test_run_tests_found_2(self, capsys, runs_dir):
        """Test path for when no tests are found for removal"""
        runner = clean.HyalusCleanRunner(runs_dir, oldest=date(2023, 2, 10), newest=date(2023, 2, 10), force=True)

        expected_fs_objs = len(list(runs_dir.iterdir())) - 1
        expected_msg = "1 old test runs have been removed"

        runner.run()

        assert expected_fs_objs == len(list(runs_dir.iterdir()))
        assert capsys.readouterr().out.strip('\n') == expected_msg

    def test_run_removal_canceled(self, capsys, runs_dir):
        """Test that when test run removal is canceled by the user no tests get removed"""
        runner = clean.HyalusCleanRunner(runs_dir)

        expected_fs_objs = len(list(runs_dir.iterdir()))
        expected_msg = "Test run removal canceled"

        with patch("builtins.input", return_value="n"):
            runner.run()

        assert expected_fs_objs == len(list(runs_dir.iterdir()))
        assert capsys.readouterr().out.strip('\n') == expected_msg
