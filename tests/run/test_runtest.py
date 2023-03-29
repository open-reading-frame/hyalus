"""Tests for the hyalus.run.runtest module"""
# pylint: disable=protected-access

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import os
from pathlib import Path
import re

import pytest

from hyalus.config import common as config_common
from hyalus.run import common as run_common, runtest

# pylint: disable=duplicate-code
OUTER_DIR = Path(__file__).parent
TEST_DIR_1 = OUTER_DIR / "test_dir_1"
TEST_DIR_2 = OUTER_DIR / "test_dir_2"


@pytest.fixture(name="runs_dir", scope="module")
def fixture_runs_dir(tmp_path_factory):
    """Module-scope temp directory"""
    return tmp_path_factory.mktemp("runs_dir")


class TestHyalusTestRunner:
    """Tests for the HyalusTestRunner class"""

    @run_common.cwd_reset
    def test_make_run_dir(self, runs_dir):
        """Test basic creation of run directory"""
        os.chdir(OUTER_DIR)

        runner = runtest.HyalusTestRunner("test_dir_1/runtest_1", runs_dir)
        run_dir = runner._make_run_dir(runner.test)

        assert re.match(r"^runtest_1_\d{4}-\d{2}-\d{2}_[a-zA-Z0-9]{8}$", run_dir.name) is not None

        assert run_dir.exists()
        assert (run_dir / config_common.CONFIG_PY).exists()
        assert (run_dir / config_common.OUTPUT_PATH).exists()
        assert (run_dir / config_common.TMP_PATH).exists()
        assert (run_dir / config_common.HYALUS_PATH).exists()

    @run_common.cwd_reset
    def test_make_run_dir_collision(self, runs_dir):
        """Test creation of run directory completes in the case of a collision"""
        os.chdir(OUTER_DIR)

        runner = runtest.HyalusTestRunner("test_dir_1/runtest_1", runs_dir)

        # Call _make_run_dir twice, second call expected to end up recursively calling it with alphanumeric_chars=1
        runner._make_run_dir(runner.test, alphanumeric_chars=0)
        run_dir = runner._make_run_dir(runner.test, alphanumeric_chars=0)

        assert re.match(r"^runtest_1_\d{4}-\d{2}-\d{2}_[a-zA-Z0-9]{1}$", run_dir.name) is not None

        assert run_dir.exists()
        assert (run_dir / config_common.CONFIG_PY).exists()
        assert (run_dir / config_common.OUTPUT_PATH).exists()
        assert (run_dir / config_common.TMP_PATH).exists()
        assert (run_dir / config_common.HYALUS_PATH).exists()

    def test_run_pass(self, runs_dir):
        """Test running a test that should have a passing result"""
        runner = runtest.HyalusTestRunner("runtest_1", runs_dir, search_dirs=[TEST_DIR_1])

        previous_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert runner.run()

        new_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert new_run_count == previous_run_count + 1

    def test_run_pass_cleanup_run(self, runs_dir):
        """Test cleanup of passing test run"""
        runner = runtest.HyalusTestRunner("runtest_1", runs_dir, search_dirs=[TEST_DIR_1], cleanup_on_pass=True)

        previous_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert runner.run()

        new_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert new_run_count == previous_run_count

    def test_run_fail(self, runs_dir):
        """Test running a test that should have a failing result"""
        runner = runtest.HyalusTestRunner("runtest_2", runs_dir, search_dirs=[TEST_DIR_1])

        previous_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert not runner.run()

        new_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert new_run_count == previous_run_count + 1

    def test_run_fail_cleanup_run(self, runs_dir):
        """Test that a failing run does not get cleaned up when the cleanup flag is set to True"""
        runner = runtest.HyalusTestRunner("runtest_2", runs_dir, search_dirs=[TEST_DIR_1], cleanup_on_pass=True)

        previous_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert not runner.run()

        new_run_count = len([sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()])

        assert new_run_count == previous_run_count + 1

    def test_run_fail_raise_exception(self, runs_dir):
        """Test failing Step with its error flag set to True causes the run to exit before executing more Steps"""
        runner = runtest.HyalusTestRunner("runtest_2", runs_dir, search_dirs=[TEST_DIR_2])

        previous_runs = [sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()]

        assert not runner.run()

        new_runs = [sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()]

        run_dir = Path(list(set(new_runs) - set(previous_runs))[0])

        # Check presence of log files to assert that the last step that was run is the one expected to error
        assert (run_dir / config_common.HYALUS_PATH / "2_RunFunctionStep_log.txt").exists()
        assert not (run_dir / config_common.HYALUS_PATH / "3_AssertEQ_log.txt").exists()

    def test_run_error(self, runs_dir):
        """Test handling of running Step that is expected to error out"""
        runner = runtest.HyalusTestRunner("runtest_3", runs_dir, search_dirs=[TEST_DIR_2])

        assert not runner.run()

    def test_run_invalid_test(self, runs_dir):
        """Test handling of running a test that is not a valid hyalus test"""
        runner = runtest.HyalusTestRunner("runtest_6", runs_dir, search_dirs=[TEST_DIR_2])

        assert not runner.run()

    def test_run_invalid_config(self, runs_dir):
        """Test handling of loading an invalid config file"""
        runner = runtest.HyalusTestRunner("runtest_5", runs_dir, search_dirs=[TEST_DIR_2])

        assert not runner.run()

    def test_run_fail_halt_on_error(self, runs_dir):
        """Test handling of running Step that is expected to fail which has halt_on_error set to True"""
        runner = runtest.HyalusTestRunner("runtest_4", runs_dir, search_dirs=[TEST_DIR_2])

        previous_runs = [sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()]

        assert not runner.run()

        new_runs = [sub_dir for sub_dir in runs_dir.iterdir() if sub_dir.is_dir()]
        run_dir = Path(list(set(new_runs) - set(previous_runs))[0])

        assert (run_dir / config_common.HYALUS_PATH / "3_AssertEQButFail_log.txt").exists()
        assert not (run_dir / config_common.HYALUS_PATH / "4_AssertEQ_log.txt").exists()
