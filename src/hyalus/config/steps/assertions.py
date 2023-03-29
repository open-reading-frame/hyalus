"""Steps related to verification of outputs/results"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import abc
from pathlib import Path
from typing import Any, Callable

from hyalus.assertions import compare
from hyalus.assertions.apply import ConstraintApplier
from hyalus.config.steps.base import StepBase, StepStatus, StepOutput
from hyalus.parse.factory import get_parser


class AssertionStep(StepBase):
    """Base class for assertions"""

    def __init__(self, *args: Any) -> None:
        """Ctor.

        :param args: Arguments to pass to the AssertionStep's comparison function
        """
        self.args = args

    def __str__(self) -> str:
        return f" {self.op_str} ".join(f"'{arg}'" if isinstance(arg, str) else str(arg) for arg in self.args)

    @property
    @abc.abstractmethod
    def op_str(self) -> str:
        """:return: String representation of the operator for the assertion, e.g. ``==``"""

    @property
    def needs(self) -> None:  # pragma: no cover
        return None

    @property
    def halt_on_failure(self) -> bool:
        """:return: False"""
        return False

    @property
    @abc.abstractmethod
    def comparison_func(self) -> Callable[..., bool]:
        """:return: The function for the AssertionStep"""

    def _pre_process(self) -> list[Any]:
        """This method is responsible for converting anything path-/index-/key-like into a corresponding data structure
        for use in comparison functions.

        :return: The processed arguments to pass to the assertion function
        """
        processed_args = []

        for arg in self.args:
            if isinstance(arg, tuple):
                if len(arg) == 2 and isinstance(arg[0], (str, Path)):
                    if (parser := get_parser(arg[0])) is not None:
                        arg = parser.search(arg[1])

            if isinstance(arg, (str, Path)):
                if (parser := get_parser(arg)) is not None:
                    arg = parser.parse()

            processed_args.append(arg)

        return processed_args

    def _run_workflow(self, pre_process_output: Any = None) -> StepOutput:
        """Run the given comparison function on given arguments and return the result

        :param pre_process_output: The output of processing arguments to the AssertionStep
        :return: The result of the comparison
        """
        result = ConstraintApplier(self.comparison_func, *pre_process_output).apply()

        if result:
            self._logger.info(f"Comparison {self} evaluated to True")
        else:
            self._logger.error(f"Comparison {self} evaluated to False")

        return StepOutput(str(self), StepStatus.get_by_bool(result))


class AssertEQ(AssertionStep):
    """Step that asserts equality for given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"=="``"""
        return "=="

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.eq`"""
        return compare.eq


class AssertNE(AssertionStep):
    """Step that asserts inequality for given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"!="``"""
        return "!="

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.ne`"""
        return compare.ne


class AssertGT(AssertionStep):
    """Step that asserts each given argument is strictly greater than the next"""

    @property
    def op_str(self) -> str:
        """:return: ``">"``"""
        return ">"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.gt`"""
        return compare.gt


class AssertGE(AssertionStep):
    """Step that asserts each given argument is greater than or equal to than the next"""

    @property
    def op_str(self) -> str:
        """:return: ``"≥"``"""
        return "≥"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.ge`"""
        return compare.ge


class AssertLT(AssertionStep):
    """Step that asserts each given argument is strictly less than the next"""

    @property
    def op_str(self) -> str:
        """:return: ``"<"``"""
        return "<"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.lt`"""
        return compare.lt


class AssertLE(AssertionStep):
    """Step that asserts each given argument is less than or equal to than the next"""

    @property
    def op_str(self) -> str:
        """:return: ``"≤"``"""
        return "≤"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.le`"""
        return compare.le


class AssertIn(AssertionStep):
    """Step that asserts the first of given arguments is in the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"in"``"""
        return "in"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.in_`"""
        return compare.in_


class AssertNotIn(AssertionStep):
    """Step that asserts the first of given arguments is not in the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"not in"``"""
        return "not in"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.not_in`"""
        return compare.not_in


class AssertContains(AssertionStep):
    """Step that asserts the first of given arguments contains the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"contains"``"""
        return "contains"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.contains`"""
        return compare.contains


class AssertDoesNotContain(AssertionStep):
    """Step that asserts the first of given arguments does not contain the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"does not contain"``"""
        return "does not contain"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.does_not_contain`"""
        return compare.does_not_contain


class AssertKeysContain(AssertionStep):
    """Step that asserts the first of given arguments' keys contains the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"keys contain"``"""
        return "keys contain"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.keys_contain`"""
        return compare.keys_contain


class AssertValuesContain(AssertionStep):
    """Step that asserts the first of given arguments' values contains the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"values contain"``"""
        return "values contain"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.values_contain`"""
        return compare.values_contain


class AssertItemsContain(AssertionStep):
    """Step that asserts the first of given arguments' items contains the second of given arguments"""

    @property
    def op_str(self) -> str:
        """:return: ``"items contain"``"""
        return "items contain"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.items_contain`"""
        return compare.items_contain


class AssertDataFrameContains(AssertionStep):
    """Step that asserts a DataFrame contains at least one record matching a list of given criteria"""

    @property
    def op_str(self) -> str:
        """:return: ``"contains"``"""
        return "contains"

    @property
    def comparison_func(self) -> Callable[..., bool]:
        """:return: :py:func:`hyalus.assertions.compare.dataframe_contains`"""
        return compare.dataframe_contains
