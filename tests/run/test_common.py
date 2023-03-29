"""Tests for the hyalus.run.common module"""
# pylint: disable=protected-access, too-many-public-methods

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import tempfile

import pytest

from hyalus import __version__
from hyalus.config import common as config_common
from hyalus.run import common as run_common

# pylint: disable=duplicate-code
OUTER_DIR = Path(__file__).parent
TEST_DIR_1 = OUTER_DIR / "test_dir_1"
TEST_DIR_2 = OUTER_DIR / "test_dir_2"
RUNS_DIR = OUTER_DIR / "runs_dir"

RUNTEST_1 = TEST_DIR_1 / "runtest_1"
RUNTEST_2 = TEST_DIR_1 / "runtest_2"
RUNTEST_7 = TEST_DIR_1 / "runtest_7"

RUNTEST_2_DUPLICATE = TEST_DIR_2 / "runtest_2"
RUNTEST_3 = TEST_DIR_2 / "runtest_3"
RUNTEST_4 = TEST_DIR_2 / "runtest_4"
RUNTEST_5 = TEST_DIR_2 / "runtest_5"
RUNTEST_6 = TEST_DIR_2 / "runtest_6"

TEST_RUN_1 = RUNS_DIR / "runtest_1_2023-02-09_ey2S4AGY"
TEST_RUN_2 = RUNS_DIR / "runtest_2_2023-02-10_ndTVVsed"
TEST_RUN_7 = RUNS_DIR / "runtest_7_2023-02-11_5KUBAvgo"


class TestHyalusTest:
    """Tests for the HyalusTest class"""

    def test_input_dir(self):
        """Test input directory path creation"""
        assert run_common.HyalusTest(TEST_RUN_1).input_dir == TEST_RUN_1 / config_common.INPUT_PATH

    def test_config(self):
        """Test config.py path creation"""
        assert run_common.HyalusTest(RUNTEST_1).config == RUNTEST_1 / "config.py"

    def test_is_valid_true(self):
        """Assert that a directory with a config.py in it that is not an old test run is treated as valid"""
        assert run_common.HyalusTest(RUNTEST_1).is_valid

    def test_is_valid_false_no_config(self):
        """Assert that a directory missing a config.py is not treated as valid"""
        assert not run_common.HyalusTest(RUNTEST_6).is_valid

    def test_is_valid_false_test_run(self):
        """Assert that an old hyalus test run is not treated as valid"""
        assert not run_common.HyalusTest(TEST_RUN_1).is_valid

    def test_matches_tags_true_any(self):
        """Test tag matching with any as the tag operator and an expected result of True"""
        hyalus_test = run_common.HyalusTest(RUNTEST_1)

        assert hyalus_test.matches_tags(["short"], any)
        assert hyalus_test.matches_tags(["functionaltest"], any)
        assert hyalus_test.matches_tags(["short", "functionaltest"], any)

    def test_matches_tags_true_all(self):
        """Test tag matching with all as the tag operator and an expected result of True"""
        hyalus_test = run_common.HyalusTest(RUNTEST_1)

        assert hyalus_test.matches_tags(["short", "functionaltest"], all)

    def test_matches_tags_true_no_tags(self):
        """Test that when no tags are given it is treated as a match"""
        hyalus_test = run_common.HyalusTest(RUNTEST_1)

        assert hyalus_test.matches_tags([], any)
        assert hyalus_test.matches_tags([], all)

    def test_matches_tags_false_missing_tags_any(self):
        """Test tag matching with any as the tag operator and an expected result of False"""
        hyalus_test = run_common.HyalusTest(RUNTEST_1)

        assert not hyalus_test.matches_tags(["bad_tag"], any)

    def test_matches_tags_false_missing_tags_all(self):
        """Test tag matching with all as the tag operator and an expected result of False"""
        hyalus_test = run_common.HyalusTest(RUNTEST_1)

        assert not hyalus_test.matches_tags(["bad_tag"], all)
        assert not hyalus_test.matches_tags(["bad_tag", "short", "functionaltest"], all)

    def test_matches_tags_false_missing_config(self):
        """Test that when handling a test without a config.py, matches_tags always returns False"""
        hyalus_test = run_common.HyalusTest(RUNTEST_6)

        assert not hyalus_test.matches_tags([], any)
        assert not hyalus_test.matches_tags([], all)

    def test_matches_tags_false_invalid_config(self):
        """Test that when handling a test with an invalid config.py, matches_tags always returns False"""
        hyalus_test = run_common.HyalusTest(RUNTEST_5)

        assert not hyalus_test.matches_tags([], any)
        assert not hyalus_test.matches_tags([], all)


class TestHyalusRun:
    """Tests for the HyalusRun class"""

    def test_config(self):
        """Test config.py path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).config == TEST_RUN_1 / config_common.CONFIG_PY

    def test_hyalus_dir(self):
        """Test hyalus directory path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).hyalus_dir == TEST_RUN_1 / config_common.HYALUS_PATH

    def test_hyalus_log(self):
        """Test hyalus/hyalus.log path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).hyalus_log == TEST_RUN_1 / config_common.HYALUS_LOG

    def test_run_metadata(self):
        """Test hyalus/run_metadata.json path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).run_metadata == TEST_RUN_1 / config_common.RUN_METADATA

    def test_input_dir(self):
        """Test input directory path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).input_dir == TEST_RUN_1 / config_common.INPUT_PATH

    def test_output_dir(self):
        """Test output directory path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).output_dir == TEST_RUN_1 / config_common.OUTPUT_PATH

    def test_tmp_dir(self):
        """Test tmp directory path creation"""
        assert run_common.HyalusRun(TEST_RUN_1).tmp_dir == TEST_RUN_1 / config_common.TMP_PATH

    def test_subdirectories(self):
        """Test that all of the expected subdirectories are listed in the subdirectories attribute"""
        test_run = run_common.HyalusRun(TEST_RUN_1)

        assert set(test_run.subdirectories) == {TEST_RUN_1 / path for path in config_common.TEST_SUBDIRS}

    def test_expected_fs_objs(self):
        """Test that the relevant directories and files are listed in the expected_fs_objs attribute"""
        test_run = run_common.HyalusRun(TEST_RUN_1)

        paths = list(config_common.TEST_SUBDIRS) + [
            config_common.CONFIG_PY,
            config_common.HYALUS_LOG,
            config_common.RUN_METADATA,
        ]

        assert set(test_run.expected_fs_objs) == {TEST_RUN_1 / path for path in paths}

    def test_test_name(self):
        """Test setting of the test_name attribute"""
        assert run_common.HyalusRun(TEST_RUN_1).test_name == "runtest_1"

    def test_test_date(self):
        """Test setting of the test_date attribute"""
        assert run_common.HyalusRun(TEST_RUN_1).test_date == date(2023, 2, 9)

    def test_randomer(self):
        """Test setting of the randomer attribute"""
        assert run_common.HyalusRun(TEST_RUN_1).randomer == "ey2S4AGY"

    def test_set_run_attrs_invalid_bad_date(self):
        """Assert a ValueError is raised when giving a run directory name with a bad date string"""
        with pytest.raises(ValueError):
            run_common.HyalusRun("test_name_2023-14-01_234nasdf").set_run_attrs()

    def test_set_run_attrs_invalid_no_randomer(self):
        """Assert a ValueError is raised when giving a run directory name missing a randomer"""
        with pytest.raises(ValueError):
            run_common.HyalusRun("test_name_2023-02-01").set_run_attrs()

    def test_set_run_attrs_invalid_hyalus_test(self):
        """Assert a ValueError is raised when giving a random test name"""
        with pytest.raises(ValueError):
            run_common.HyalusRun("test_name").set_run_attrs()

    def test_write_run_metadata(self, run_dir):
        """Assert run metadata is written as expected to the run_metadata.json file"""
        run_dir.write_run_metadata()

        with open(run_dir.run_metadata, 'r', encoding="utf-8") as metadata_fh:
            metadata = json.load(metadata_fh)

        assert metadata["version"] == __version__

        run_start = datetime.strptime(metadata["run_start"], f"{run_common.DATE_FMT} {run_common.TIME_FMT}")

        # We just wrote the file - check the written datetime compared to now is less than 5 seconds
        assert datetime.now() - run_start < timedelta(seconds=5)

    def test_is_valid_true(self):
        """Test that a test run with a valid name and expected files and directories is treated as valid"""
        assert run_common.HyalusRun(TEST_RUN_1).is_valid

    def test_is_valid_false_bad_name(self):
        """Test that a test run with a bad name is treated as invalid"""
        assert not run_common.HyalusRun("bad_name").is_valid

    def test_is_valid_false_missing_fs_obj(self):
        """Test that a test run missing expected files/directories is treated as invalid"""
        assert not run_common.HyalusRun("good_name_2023-02-01_randomer").is_valid

    def test_within_date_range_true_lt_eq(self):
        """Test the within_date_range with oldest < test_date == newest"""
        assert run_common.HyalusRun(TEST_RUN_1).within_date_range(date(2023, 2, 8), date(2023, 2, 9))

    def test_within_date_range_true_eq_gt(self):
        """Test the within_date_range with oldest == test_date < newest"""
        assert run_common.HyalusRun(TEST_RUN_1).within_date_range(date(2023, 2, 9), date(2023, 2, 10))

    def test_within_date_range_true_eq_eq(self):
        """Test the within_date_range with oldest == test_date == newest"""
        assert run_common.HyalusRun(TEST_RUN_1).within_date_range(date(2023, 2, 9), date(2023, 2, 9))

    def test_within_date_range_false_lt_lt(self):
        """Test the within_date_range with a date greater than the given range"""
        assert not run_common.HyalusRun(TEST_RUN_1).within_date_range(date(2023, 2, 8), date(2023, 2, 8))

    def test_within_date_range_false_gt_gt(self):
        """Test the within_date_range with a date less than the given range"""
        assert not run_common.HyalusRun(TEST_RUN_1).within_date_range(date(2023, 2, 10), date(2023, 2, 10))


class TestCwdReset:
    """Tests for the cwd_reset decorator"""

    def test_cwd_reset_function_successful(self):
        """Test the cwd_reset decorator properly executes a function and resets the working directory"""

        @run_common.cwd_reset
        def chdir_and_return_arg(directory, arg):
            os.chdir(directory)
            assert os.getcwd() == directory
            return arg

        cwd_at_start = os.getcwd()

        assert chdir_and_return_arg(str(OUTER_DIR), 5) == 5

        assert os.getcwd() == cwd_at_start

    def test_cwd_reset_function_exception(self):
        """Test the cwd_reset decorator resets the directory when an Exception is raised in the decorated function"""

        @run_common.cwd_reset
        def chdir_and_raise_exception(directory):
            os.chdir(directory)
            assert os.getcwd() == directory
            raise KeyError("🔑")

        cwd_at_start = os.getcwd()

        with pytest.raises(KeyError):
            assert chdir_and_raise_exception(str(OUTER_DIR))

        assert os.getcwd() == cwd_at_start


class TestMakeRunDir:
    """Tests for the make_run_dir utility function"""

    def test_no_preexisting_outer_dir(self):
        """Tests that outer directory creation is handled when it does not exist"""
        path = Path(tempfile.mkdtemp()) / "sub_dir"

        run_common.make_run_dir(path)

        assert path.is_dir()

    def test_all_created(self, tmp_path):
        """Test that all run directory subdirectories are created when none exist beforehand"""
        run_common.make_run_dir(tmp_path)

        for path in (tmp_path / "output", tmp_path / "tmp", tmp_path / "hyalus"):
            assert path.is_dir()

    def test_existing_untouched(self, tmp_path):
        """Test that if given a run directory that already has some subdirectories they are left untouched"""
        for path in (config_common.OUTPUT_PATH, config_common.HYALUS_PATH):
            subdir = tmp_path / path
            subdir.mkdir()
            (subdir / "dummy_file.txt").touch()

        run_common.make_run_dir(tmp_path)

        for path in config_common.TEST_SUBDIRS:
            subdir = tmp_path / path
            assert subdir.is_dir()

        for path in (config_common.OUTPUT_PATH, config_common.HYALUS_PATH):
            file = tmp_path / path / "dummy_file.txt"
            assert file.is_file()


class TestParseTestSuite:
    """Tests for the _parse_test_suite helper function"""

    def test_successfull_parse(self):
        """Test proper parsing of test suite file, including ignoring comments and empty lines"""
        assert run_common._parse_test_suite(TEST_DIR_2 / "suite_2.ste") == ["suite_1.ste", "runtest_3", "runtest_4"]

    def test_invalid_parse(self):
        """Make sure a proper exception is raised when given a test suite that can't be parsed"""
        with pytest.raises(run_common.InvalidTestSuite):
            run_common._parse_test_suite(RUNTEST_1)


class TestFindFsObj:
    """Tests for the find_fs_obj utility function"""

    @run_common.cwd_reset
    def test_find_fs_obj_cwd(self):
        """Test finding filesystem object in the current working directory"""
        os.chdir(TEST_DIR_1)

        assert run_common.find_fs_obj("runtest_1") == RUNTEST_1

    @run_common.cwd_reset
    def test_find_fs_obj_relative_path(self):
        """Test finding filesystem object when it is a relative path from the current working directory"""
        os.chdir(OUTER_DIR)

        assert run_common.find_fs_obj("test_dir_1/runtest_1") == RUNTEST_1

    def test_find_fs_obj_absolute_path(self):
        """Test finding filesystem object when it is an absolute path"""
        assert run_common.find_fs_obj(RUNTEST_1) == RUNTEST_1

    def test_find_fs_obj_absolute_path_multiple_search_dirs(self):
        """Test handling absolute paths when multiple search directories are given"""
        test_name = RUNTEST_1
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        assert run_common.find_fs_obj(test_name, search_dirs=search_dirs) == test_name

    @run_common.cwd_reset
    def test_find_fs_obj_in_search_dirs_relative_path(self):
        """Test finding filesystem object when it lives in one of the given relative path search directories"""
        os.chdir(OUTER_DIR)

        test_name = "runtest_1"
        search_dirs = [Path("test_dir_1"), Path("test_dir_2")]

        assert run_common.find_fs_obj(test_name, search_dirs=search_dirs) == RUNTEST_1

    def test_find_fs_obj_in_search_dirs_absolute_path(self):
        """Test finding filesystem object when it lives in one of the given absolute path search directories"""
        test_name = "runtest_1"
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        assert run_common.find_fs_obj(test_name, search_dirs=search_dirs) == RUNTEST_1

    def test_find_fs_obj_not_found(self):
        """Test that when giving something that does not exist in cwd or any search dirs, NotFound is raised"""
        test_name = "runtest_999"
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        match = f"Could not find item {test_name} in directories: {TEST_DIR_1}, {TEST_DIR_2}"

        with pytest.raises(run_common.NotFound, match=match):
            run_common.find_fs_obj(test_name, search_dirs=search_dirs)

    def test_find_fs_obj_duplicate(self):
        """Test that when a filesystem object is found in multiple search dirs, DuplicateTests is raised"""
        test_name = "runtest_2"
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        match = f"Found multiple items with name {test_name}: {RUNTEST_2}, {RUNTEST_2_DUPLICATE}"

        with pytest.raises(run_common.Duplicate, match=match):
            run_common.find_fs_obj(test_name, search_dirs=search_dirs)


def test_find_all_tests():
    """Assert that find_all_tests returns absolute paths to all tests based on given search directories"""
    search_dirs = [TEST_DIR_1, TEST_DIR_2]

    expected = {RUNTEST_1, RUNTEST_2, RUNTEST_7, RUNTEST_2_DUPLICATE, RUNTEST_3, RUNTEST_4, RUNTEST_5}

    assert run_common.find_all_tests(search_dirs) == expected


class TestFindTestsByName:
    """Tests for the find_tests_by_name function"""

    def test_list_of_test_names(self):
        """Test handling of only test names"""
        test_names = ["runtest_1", "runtest_3"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        expected = {RUNTEST_1, RUNTEST_3}

        assert run_common.find_tests_by_name(test_names, search_dirs) == expected

    def test_list_of_tests_suites(self):
        """Test handling of only test suites"""
        test_suites = ["suite_1.ste", "suite_2.ste"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        expected = {RUNTEST_1, RUNTEST_3, RUNTEST_4}

        assert run_common.find_tests_by_name(test_suites, search_dirs) == expected

    def test_mixed_list(self):
        """Test handling of a mix of test name and suite"""
        inputs = ["runtest_3", "suite_1.ste"]
        search_dirs = [TEST_DIR_1, TEST_DIR_2]

        expected = {RUNTEST_1, RUNTEST_3}

        assert run_common.find_tests_by_name(inputs, search_dirs) == expected

    def test_suite_with_wrong_ext(self):
        """Make sure if a file is given with the expected suite extension, a InvalidTestSuite Exception is raised"""
        inputs = ["suite_bad_ext.txt"]
        search_dirs = [TEST_DIR_1]

        with pytest.raises(run_common.InvalidTestSuite):
            run_common.find_tests_by_name(inputs, search_dirs)


class TestFindTestsByTag:
    """Tests for the find_tests_by_tag function"""

    def test_all_tag_op(self):
        """Test proper handling of matched tags when using all as the tag operator"""
        tags = ["Short", "FunctionalTest"]
        tag_op = all
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        expected = {RUNTEST_1}

        assert run_common.find_tests_by_tag(tags, tag_op, search_dirs) == expected

    def test_any_tag_op(self):
        """Test proper handling of matched tags when using any as the tag operator"""
        tags = ["Medium", "RegressionTest"]
        tag_op = any
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        expected = {RUNTEST_2, RUNTEST_3}

        assert run_common.find_tests_by_tag(tags, tag_op, search_dirs) == expected

    def test_no_match(self):
        """Test that when we don't expect any tests to match, we get the empty set back"""
        tags = ["Short", "IntegrationTest"]
        tag_op = all
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        expected = set()

        assert run_common.find_tests_by_tag(tags, tag_op, search_dirs) == expected

    def test_no_tags(self):
        """Test that if we don't send in any tags to find, we don't get any tests out"""
        tags = []
        tag_op = any
        search_dirs = [TEST_DIR_1, TEST_DIR_2]
        expected = set()

        assert run_common.find_tests_by_tag(tags, tag_op, search_dirs) == expected


class TestFindTestRuns:
    """Tests for the find_test_runs utility method"""

    def test_find_test_names(self):
        """Assert that when test names are specified, test runs are subset to those matching the test names"""
        assert run_common.find_test_runs(RUNS_DIR, test_names=["runtest_1", "runtest_7"]) == {TEST_RUN_1, TEST_RUN_7}

    def test_find_no_test_names(self):
        """Assert that when no test names are given, all test runs in the given directory are returned"""
        assert run_common.find_test_runs(RUNS_DIR) == {TEST_RUN_1, TEST_RUN_2, TEST_RUN_7}


class TestFindRelevantTestRuns:
    """Tests for the find_relevant_test_runs utility function"""

    def test_no_args(self):
        """Test that all test runs are returned when not giving tags or a date range to match"""
        expected = {TEST_RUN_1, TEST_RUN_2, TEST_RUN_7}
        observed = run_common.find_relevant_test_runs(RUNS_DIR)

        assert expected == observed

    def test_test_names_only(self):
        """Test that when only giving test names to match, expected test runs are returned"""
        test_names = ["runtest_1", "runtest_2", "runtest_3"]

        expected = {TEST_RUN_1, TEST_RUN_2}
        observed = run_common.find_relevant_test_runs(RUNS_DIR, test_names=test_names)

        assert expected == observed

    def test_match_tags_only(self):
        """Test that when only giving tags to match, expected test runs are returned"""
        tags = ["medium", "long"]
        tag_op = any

        expected = {TEST_RUN_2, TEST_RUN_7}
        observed = run_common.find_relevant_test_runs(RUNS_DIR, match_tags=tags, tag_op=tag_op)

        assert expected == observed

    def test_date_range_only(self):
        """Test that when only giving a date range to match, expected test runs are returned"""
        oldest = date(2023, 2, 10)
        newest = date(2023, 2, 11)

        expected = {TEST_RUN_2, TEST_RUN_7}
        observed = run_common.find_relevant_test_runs(RUNS_DIR, oldest=oldest, newest=newest)

        assert expected == observed

    def test_test_names_and_match_tags(self):
        """Test that when giving both test names and tags to match, expected rest runs are returned"""
        test_names = ["runtest_1", "runtest_5", "runtest_7"]
        tags = ["medium", "long"]
        tag_op = any

        expected = {TEST_RUN_7}
        observed = run_common.find_relevant_test_runs(RUNS_DIR, test_names=test_names, match_tags=tags, tag_op=tag_op)

        assert expected == observed

    def test_test_names_and_date_range(self):
        """Test that when giving both test names and a date range to match, expected test runs are returned"""
        test_names = ["runtest_1", "runtest_5", "runtest_7"]
        oldest = date(2023, 2, 9)
        newest = date(2023, 2, 10)

        expected = {TEST_RUN_1}
        observed = run_common.find_relevant_test_runs(RUNS_DIR, test_names=test_names, oldest=oldest, newest=newest)

        assert expected == observed

    def test_match_tags_and_date_range(self):
        """Test that when giving both tags and a date range to match, expected test runs are returned"""
        tags = ["short", "regressiontest"]
        tag_op = any
        oldest = date(2023, 2, 9)
        newest = date(2023, 2, 10)

        expected = {TEST_RUN_1, TEST_RUN_2}
        observed = run_common.find_relevant_test_runs(
            RUNS_DIR, match_tags=tags, tag_op=tag_op, oldest=oldest, newest=newest
        )

        assert expected == observed

    def test_all_args(self):
        """Test when giving all possible arguments, expected test runs are returned"""
        test_names = ["runtest_1", "runtest_2", "runtest_4"]
        tags = ["short", "medium"]
        tag_op = any
        oldest = date(2023, 2, 10)
        newest = date(2023, 2, 15)

        expected = {TEST_RUN_2}
        observed = run_common.find_relevant_test_runs(
            RUNS_DIR, test_names=test_names, match_tags=tags, tag_op=tag_op, oldest=oldest, newest=newest
        )

        assert expected == observed
