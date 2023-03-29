"""Unit tests for the hyalus.config.steps.base module"""
# pylint: disable=protected-access

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from typing import Any

from hyalus.config.steps import base


class MyStep(base.StepBase):
    """For use in unit testing of the StepBase class"""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    @property
    def needs(self) -> list[str] | None:
        return None

    def _run_workflow(self, pre_process_output: Any = None) -> base.StepOutput:
        return base.StepOutput("", base.StepStatus.PASS)


def test_load(run_dir):
    """Ensure after running the _load method that relevant attributes have been set"""
    step = MyStep()
    step._load(5, run_dir)

    assert step.step_number == 5
    assert step.run_dir == run_dir
    assert step.input_dir == run_dir / "input"
    assert step.output_dir == run_dir / "output"
    assert step.tmp_dir == run_dir / "tmp"
    assert step.hyalus_dir == run_dir / "hyalus"
    assert step.hyalus_log == step.hyalus_dir / "hyalus.log"
    assert step.step_log == step.hyalus_dir / "5_MyStep_log.txt"
