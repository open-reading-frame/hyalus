"""Tests for the hyalus.run.list module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path

import hyalus.run.list as hyalus_list

# pylint: disable=duplicate-code
OUTER_DIR = Path(__file__).parent
TEST_DIR_1 = OUTER_DIR / "test_dir_1"
TEST_DIR_2 = OUTER_DIR / "test_dir_2"


class TestHyalusListRunner:
    """Tests for the HyalusListRunner class"""

    def test_list_all(self, capsys):
        """Test listing of all tests within the given search directories"""
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        runner = hyalus_list.HyalusListRunner(search_dirs=search_dirs)

        runner.run()

        expected = ["runtest_1", "runtest_2", "runtest_3", "runtest_4", "runtest_5", "runtest_7"]

        assert capsys.readouterr().out.strip('\n').split('\n') == expected

    def test_list_by_tag_all(self, capsys):
        """Test listing of tests matching given given with all as the tag operator"""
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        tags = ["Short", "FunctionalTest"]
        tag_op = all

        runner = hyalus_list.HyalusListRunner(search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        runner.run()

        expected = ["runtest_1"]

        assert capsys.readouterr().out.strip('\n').split('\n') == expected

    def test_list_by_tag_any(self, capsys):
        """Test listing of tests matching given given with any as the tag operator"""
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        tags = ["RegressionTest", "FunctionalTest"]
        tag_op = any

        runner = hyalus_list.HyalusListRunner(search_dirs=search_dirs, tags=tags, tag_op=tag_op)

        runner.run()

        expected = ["runtest_1", "runtest_2", "runtest_3"]

        assert capsys.readouterr().out.strip('\n').split('\n') == expected
