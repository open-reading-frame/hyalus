"""Tests for the hyalus.run.runsuite module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path

import pytest

from hyalus.run.runsuite import HyalusSuiteRunner, NoTestsFound

# pylint: disable=duplicate-code
OUTER_DIR = Path(__file__).parent
TEST_DIR_1 = OUTER_DIR / "test_dir_1"
TEST_DIR_2 = OUTER_DIR / "test_dir_2"


@pytest.fixture(name="runs_dir", scope="module")
def fixture_runs_dir(tmp_path_factory):
    """Module-scope temp directory"""
    return tmp_path_factory.mktemp("runs_dir")


class TestHyalusSuiteRunner:
    """Tests for the HyalusSuiteRunner class"""

    def test_get_tests_by_test_name(self):
        """Tests test retrieval via test name"""
        to_run = ["runtest_1", "runtest_7"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        expected = [TEST_DIR_1 / "runtest_1", TEST_DIR_1 / "runtest_7"]

        runner = HyalusSuiteRunner(to_run=to_run, search_dirs=search_dirs)

        assert set(runner.get_tests()) == set(expected)

    def test_get_tests_by_test_suite(self):
        """Tests test retrieval via test suite"""
        to_run = ["pass.ste", "fail.ste"]
        search_dirs = [TEST_DIR_1]
        expected = [TEST_DIR_1 / "runtest_1", TEST_DIR_1 / "runtest_7", TEST_DIR_1 / "runtest_2"]

        runner = HyalusSuiteRunner(to_run=to_run, search_dirs=search_dirs)

        assert set(runner.get_tests()) == set(expected)

    def test_get_tests_by_tags(self):
        """Tests test retrieval via tags"""
        search_dirs = [TEST_DIR_1]
        tags = ["Short", "Medium"]
        tag_op = any
        expected = [TEST_DIR_1 / "runtest_1", TEST_DIR_1 / "runtest_2"]

        runner = HyalusSuiteRunner(search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        assert set(runner.get_tests()) == set(expected)

    def test_get_tests_by_all(self):
        """Tests test retrieval via test name, test suite, and tags - also tests handling of duplicates"""
        to_run = ["runtest_1", "pass.ste"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        tags = ["FunctionalTest", "Medium", "Long", "EndToEndTest"]
        tag_op = any
        expected = [
            TEST_DIR_1 / "runtest_1",
            TEST_DIR_1 / "runtest_2",
            TEST_DIR_1 / "runtest_7",
            TEST_DIR_2 / "runtest_4",
        ]

        runner = HyalusSuiteRunner(to_run=to_run, search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        assert set(runner.get_tests()) == set(expected)

    def test_run_test_names_pass(self, runs_dir):
        """Test running via multiple test names, all tests expected to pass so overall result should be True"""
        to_run = ["runtest_1", "runtest_7"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert runner.run()

    def test_run_test_names_fail(self, runs_dir):
        """Test running via multiple test names, 1 test should pass and 1 should fail, overall result should be False"""
        to_run = ["runtest_1", "runtest_2"]
        search_dirs = [TEST_DIR_1]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert not runner.run()

    def test_run_test_names_error(self, runs_dir):
        """Test running tests that are expected to error out, asserting the overall result is False"""
        to_run = ["runtest_3", "runtest_4"]
        search_dirs = [TEST_DIR_2]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert not runner.run()

    def test_run_suite_file_pass(self, runs_dir):
        """Test running tests that are all expected to pass via suite file"""
        to_run = ["pass.ste"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert runner.run()

    def test_run_suite_file_fail(self, runs_dir):
        """Test running tests that are expected to fail via suite file"""
        to_run = ["fail.ste"]
        search_dirs = [TEST_DIR_1]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert not runner.run()

    def test_run_suite_file_error(self, runs_dir):
        """Test running tests that are expected to error via suite file"""
        to_run = ["error.ste"]
        search_dirs = [TEST_DIR_2]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert not runner.run()

    def test_run_tags_pass(self, runs_dir):
        """Test running tests that are expected to pass via tag collection"""
        search_dirs = [TEST_DIR_1]
        tags = ["Short", "Long"]
        tag_op = any

        runner = HyalusSuiteRunner(runs_dir=runs_dir, search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        assert runner.run()

    def test_run_tags_fail(self, runs_dir):
        """Test running tests that are expected to fail via tag collection"""
        search_dirs = [TEST_DIR_1]
        tags = ["Medium", "RegressionTest"]
        tag_op = all

        runner = HyalusSuiteRunner(runs_dir=runs_dir, search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        assert not runner.run()

    def test_run_tags_error(self, runs_dir):
        """Test running tests that are expected to error via tag collection"""
        search_dirs = [TEST_DIR_2]
        tags = ["RegressionTest", "EndToEndTest"]
        tag_op = any

        runner = HyalusSuiteRunner(runs_dir=runs_dir, search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        assert not runner.run()

    def test_run_test_names_suite_and_tags(self, runs_dir):
        """Test running tests via combination of name, suite, and tags"""
        to_run = ["runtest_7", "pass.ste"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        tags = ["EndToEndTest"]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs, tags=tags)

        assert not runner.run()

    def test_run_no_tests_found(self, runs_dir):
        """Test short circuiting when given inputs result in no tests to run"""
        to_run = []
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        with pytest.raises(NoTestsFound):
            runner.run()

    def test_runtest_with_bad_input(self, runs_dir):
        """In the unlikely event of somehow passing HyalusTestRunner invalid input, assert we fail the overall run"""
        to_run = ["runtest_7", "pass.ste"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        runner = HyalusSuiteRunner(to_run=to_run, runs_dir=runs_dir, search_dirs=search_dirs)

        assert not runner.run_test(3)
