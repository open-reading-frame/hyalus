"""Steps related to running arbitrary pieces of code via a CLI or method/function call"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
import subprocess
import traceback
from typing import Callable, Any

from hyalus.config.common import HYALUS_PATH
from hyalus.config.steps.base import StepBase, StepStatus, StepOutput


class SubprocessStep(StepBase):
    """Step for running arbitrary shell processes/scripts"""

    def __init__(self, cmd: list[str], **kwargs: Any) -> None:
        """Ctor.

        :param cmd: The command to execute
        :param kwargs: Keyword arguments to pass to the subprocess call
        """
        self.cmd = cmd
        self.kwargs = kwargs
        self.kwargs["capture_output"] = True
        self.kwargs["check"] = False

        self.returncode: int = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.cmd}, {self.kwargs})"

    @property
    def needs(self) -> None:  # pragma: no cover
        return None

    def _run_workflow(self, pre_process_output: Any = None) -> StepOutput:
        self._logger.debug(f"Executing command {self.cmd} with **kwargs {self.kwargs}")

        result = subprocess.run(self.cmd, **self.kwargs)  # pylint: disable=subprocess-run-check
        self.returncode = result.returncode

        if (status := StepStatus(result.returncode)) is StepStatus.PASS:
            decoded = result.stdout.decode("utf-8")
            self._logger.info(f"Command {self.cmd} executed successfully")
        else:
            decoded = result.stderr.decode("utf-8")
            self._logger.error(f"Command {self.cmd} failed with the following traceback:\n{decoded}")

        return StepOutput(decoded, status)


class RunFunctionStep(StepBase):
    """Step for running an arbitrary python function. Any imported functionality MUST be imported within the function"""

    def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """Ctor.

        :param func: The function to execute
        :param args: Positional arguments to pass to the given function
        :param kwargs: Keyword arguments to pass to the given function
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs

        self.script_file: Path

    def __str__(self) -> str:
        if self.args or self.kwargs:
            return f"{self.__class__.__name__}({self.func.__name__}, {self._get_arg_str()})"

        return f"{self.__class__.__name__}({self.func.__name__})"

    @property
    def needs(self) -> None:  # pragma: no cover
        return None

    def _load(self, *args) -> None:
        """Load arguments for running the Step and set up funcstep.py file

        :param args: Positional arguments to pass to the parent class' _load method
        """
        super()._load(*args)

        self.script_file = self.run_dir / HYALUS_PATH / f"{self.step_number}_funcstep.py"

    def _get_arg_str(self) -> str:
        """Create string representing arguments to the given function based on given args and kwargs

        :return: The generated arg string
        """
        if self.args and self.kwargs:
            return f"*{self.args}, **{self.kwargs}"

        if self.args:
            return f"*{self.args}"

        if self.kwargs:
            return f"**{self.kwargs}"

        return ""

    def _run_workflow(self, pre_process_output: Any = None) -> StepOutput:
        """Execute the generated script and capture output/raised Exceptions accordingly"""
        self._logger.debug(f"Executing function {self.func.__name__} with *args {self.args} and **kwargs {self.kwargs}")

        try:
            result = self.func(*self.args, **self.kwargs)
            output = StepOutput(result, StepStatus.PASS)
            self._logger.info(f"Function {self.func.__name__} executed successfully")
        except AssertionError:
            exc = traceback.format_exc()
            output = StepOutput(exc, StepStatus.FAIL)
            self._logger.error(f"Function {self.func.__name__} failed an assertion:\n{exc}")
        except Exception:  # pylint: disable=broad-except
            exc = traceback.format_exc()
            output = StepOutput(exc, StepStatus.ERROR)
            self._logger.error(f"Function {self.func.__name__} failed with the following traceback:\n{exc}")

        return output
