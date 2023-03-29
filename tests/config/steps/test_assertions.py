"""Unit tests for the hyalus.config.steps.assertions module"""
# pylint: disable=protected-access

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
import shutil

import pandas as pd
import pytest

from hyalus.config.steps import base, assertions

DATA_PATH = Path(__file__).parent / "data"


@pytest.fixture(name="json_file")
def fixture_json_file(tmp_path):
    """Copies the verify.json file to temp directory and returns path to it"""
    shutil.copy2(DATA_PATH / "verify.json", tmp_path)
    return tmp_path / "verify.json"


@pytest.fixture(name="empty_json")
def fixture_empty_json(tmp_path):
    """Copies the empty.json file to temp directory and returns path to it"""
    shutil.copy2(DATA_PATH / "empty.json", tmp_path)
    return tmp_path / "empty.json"


@pytest.fixture(name="tsv_file")
def fixture_tsv_file(tmp_path):
    """Copies the verify.tsv file to temp directory and returns path to it"""
    shutil.copy2(DATA_PATH / "verify.tsv", tmp_path)
    return tmp_path / "verify.tsv"


class TestAssertionStep:
    """Tests for the AssertionStep class - uses AssertEQ and assumes that AssertEQ is implemented correctly"""

    def test_pre_process_no_parsers(self):
        """Tests that arguments that should not be handled as potential paths are handled correctly"""
        step = assertions.AssertEQ(3, (2, 1), ("a/path/to/file/that/will/never/exist.not_an_extension", 4))

        assert step._pre_process() == [3, (2, 1), ("a/path/to/file/that/will/never/exist.not_an_extension", 4)]

    def test_pre_process_with_parser(self, json_file):
        """Tests that a mix of arguments is handled correctly"""
        step = assertions.AssertEQ(3, (2, 1), (json_file, ["values", 0, "1"]))

        assert step._pre_process() == [3, (2, 1), 1]

    def test_pre_process_multiple_parsers(self, empty_json, tsv_file):
        """Tests that multiple path arguments are handled together properly"""
        step = assertions.AssertEQ(empty_json, (tsv_file, ("col2", "4")))

        output = step._pre_process()
        assert output[0] == {}
        assert output[1].equals(pd.DataFrame([["key1", "4", 1]], columns=["col1", "col2", "col3"]))

    def test_run_workflow_pass(self, json_file, run_dir):
        """Tests that a passing function output is handled accordingly"""
        step = assertions.AssertEQ((json_file, ["values", 0, "1"]), (json_file, ["values", 1, "2"]))

        assert step.run(3, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_workflow_fail(self, json_file, run_dir):
        """Tests that an failing function output is handled accordingly"""
        step = assertions.AssertEQ((json_file, ["values", 0, "1"]), (json_file, ["values", 1, "1"]))

        assert step.run(3, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertEQ:
    """Tests for the AssertEQ class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertEQ((json_file, ["values", 0]), 3)

        assert str(step) == f"{(Path(json_file), ['values', 0])} == 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertEQ(1, 1, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertEQ(1, 2, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertNE:
    """Tests for the AssertNE class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertNE((json_file, ["values", 0]), 3)

        assert str(step) == f"{(Path(json_file), ['values', 0])} != 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertNE(1, 2, 3)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertNE(1, 2, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertGT:
    """Tests for the AssertGT class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertGT((json_file, ["values", 0]), 3)

        assert str(step) == f"{(Path(json_file), ['values', 0])} > 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertGT(3, 2, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertGT(3, 2, 2)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertGE:
    """Tests for the AssertGE class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertGE((json_file, ["values", 0]), 3)

        assert str(step) == f"{(Path(json_file), ['values', 0])} ≥ 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertGE(2, 1, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertGE(2, 2, 3)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertLT:
    """Tests for the AssertLT class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertLT((json_file, ["values", 0]), 3)

        assert str(step) == f"{(Path(json_file), ['values', 0])} < 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertLT(1, 2, 3)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertLT(1, 2, 2)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertLE:
    """Tests for the AssertLE class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertLE((json_file, ["values", 0]), 3)

        assert str(step) == f"{(Path(json_file), ['values', 0])} ≤ 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertLE(1, 1, 2)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertLE(1, 2, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertIn:
    """Tests for the AssertIn class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertIn(3, (json_file, ["values"]))

        assert str(step) == f"3 in {(Path(json_file), ['values'])}"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertIn(1, [1, 2, 3])

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertIn(1, [2, 3, 4])

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertNotIn:
    """Tests for the AssertNotIn class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertNotIn(3, (json_file, ["values"]))

        assert str(step) == f"3 not in {(Path(json_file), ['values'])}"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertNotIn(1, [2, 3, 4])

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertNotIn(1, [1, 2, 3])

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertContains:
    """Tests for the AssertContains class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertContains((json_file, ["values"]), 3)

        assert str(step) == f"{(Path(json_file), ['values'])} contains 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertContains([1, 2, 3], 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertContains([2, 3, 4], 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertDoesNotContain:
    """Tests for the AssertDoesNotContain class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertDoesNotContain((json_file, ["values"]), 3)

        assert str(step) == f"{(Path(json_file), ['values'])} does not contain 3"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertDoesNotContain([1, 2, 3], 4)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertDoesNotContain([2, 3, 4], 2)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertContain:
    """Tests for the AssertContain class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertKeysContain((json_file, ["values", 0]), "1")

        assert str(step) == f"{(Path(json_file), ['values', 0])} keys contain '1'"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertKeysContain({"1": 1, "2": 2}, "1")

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertKeysContain({"1": 1, "2": 2}, 1)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertValuesContain:
    """Tests for the AssertValuesContain class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertValuesContain((json_file, ["values", 0]), 2)

        assert str(step) == f"{(Path(json_file), ['values', 0])} values contain 2"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertValuesContain({"1": 1, "2": 2}, 2)

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertValuesContain({"1": 1, "2": 2}, "1")

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertItemsContain:
    """Tests for the AssertItemsContain class"""

    def test_str(self, json_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertItemsContain((json_file, ["values", 0]), ("1", 1))

        assert str(step) == f"{(Path(json_file), ['values', 0])} items contain ('1', 1)"

    def test_run_pass(self, run_dir):
        """End-to-end style test for passing check"""
        step = assertions.AssertItemsContain({"1": 1, "2": 2}, ("1", 1))

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir):
        """End-to-end style test for failing check"""
        step = assertions.AssertItemsContain({"1": 1, "2": 2}, ("1", 2))

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)


class TestAssertDataFrameContains:
    """Tests for the AssertDataFrameContains class"""

    def test_str(self, tsv_file):
        """Test that string creation is functioning as intended"""
        step = assertions.AssertDataFrameContains((tsv_file, ("col1", 1)), ("col2", 2))

        assert str(step) == f"{(Path(tsv_file), ('col1', 1))} contains ('col2', 2)"

    def test_run_pass(self, run_dir, tsv_file):
        """End-to-end style test for passing check"""
        step = assertions.AssertDataFrameContains(tsv_file, ("col2", "4"))

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.PASS)

    def test_run_fail(self, run_dir, tsv_file):
        """End-to-end style test for failing check"""
        step = assertions.AssertDataFrameContains((tsv_file, ("col1", "key1")), ("col2", "6.2"))

        assert step.run(1, run_dir) == base.StepOutput(str(step), base.StepStatus.FAIL)
