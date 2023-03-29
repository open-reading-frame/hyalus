"""Unit tests for the hyalus.config.steps.run module"""
# pylint: disable=protected-access

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.config.common import HYALUS_PATH
from hyalus.config.steps import base, run


class TestSubprocessStep:
    """Unit tests for the SubprocessStep class"""

    def test_run_pass(self, run_dir):
        """Test running a command that should be successful"""
        step = run.SubprocessStep(["ls", run_dir], timeout=1.0)
        result = step.run(5, run_dir)

        assert result.output == "hyalus\noutput\ntmp\n"
        assert result.status is base.StepStatus.PASS

    def test_run_fail(self, run_dir):
        """Test running a command that should fail"""
        step = run.SubprocessStep(["ls", f"{run_dir}/not_a_dir"], timeout=1.0)
        result = step.run(5, run_dir)

        assert result.output.endswith("No such file or directory\n")
        assert result.status is base.StepStatus.ERROR

    def test_str(self, run_dir):
        """Test __str__ method"""
        step = run.SubprocessStep(["ls", str(run_dir)], timeout=1.0)

        cmd_str = f"['ls', '{run_dir}']"
        kwarg_str = "{'timeout': 1.0, 'capture_output': True, 'check': False}"

        assert str(step) == f"SubprocessStep({cmd_str}, {kwarg_str})"


def func_to_run(arg1, arg2, kwarg1=None, kwarg2=None, recurse_flip_flopped=False):
    """For testing functions with both positional and keyword args"""
    if arg1 and arg2 and kwarg1 and kwarg2:
        raise Exception("All args were truthy")

    if recurse_flip_flopped:
        return func_to_run(not arg1, not arg2, kwarg1=not kwarg1, kwarg2=not kwarg2)

    return "Function ran successfully"


class TestRunFunctionStep:
    """Unit tests for the RunFunctionStep"""

    def test_str_with_arg_str(self):
        """Test __str__ method when arguments are being passed to a function"""
        step = run.RunFunctionStep(func_to_run, True, False, kwarg1=True)

        assert str(step) == "RunFunctionStep(func_to_run, *(True, False), **{'kwarg1': True})"

    def test_str_no_arg_str(self):
        """Test __str__ method when arguments are not being passed to a function"""
        step = run.RunFunctionStep(bool)

        assert str(step) == "RunFunctionStep(bool)"

    def test_load(self, run_dir):
        """Make sure script file is properly set up after loading in args"""
        step = run.RunFunctionStep(bool)
        step._load(3, run_dir)

        assert step.script_file == run_dir / HYALUS_PATH / "3_funcstep.py"

    def test_get_arg_str_args_only(self):
        """Test arg string creation when only giving positional args"""
        step = run.RunFunctionStep(func_to_run, True, False)

        assert step._get_arg_str() == "*(True, False)"

    def test_get_arg_str_kwargs_only(self):
        """Test arg string creation when only giving keyword args"""
        step = run.RunFunctionStep(func_to_run, kwarg1=True, kwarg2=True)

        assert step._get_arg_str() == "**{'kwarg1': True, 'kwarg2': True}"

    def test_get_arg_str_args_and_kwargs(self):
        """Test arg string creation when giving both positional args and keyword args"""
        step = run.RunFunctionStep(func_to_run, True, False, kwarg1=True, kwarg2=True)

        assert step._get_arg_str() == "*(True, False), **{'kwarg1': True, 'kwarg2': True}"

    def test_get_arg_str_no_args_or_kwargs(self):
        """Test arg string creation when no args are given"""
        step = run.RunFunctionStep(bool)

        assert step._get_arg_str() == ""

    def test_run_pass(self, run_dir):
        """Make sure stdout is captured and a return code of 0 is returned when a function runs successfully"""
        step = run.RunFunctionStep(func_to_run, True, False, kwarg1=True, kwarg2=True)
        result = step.run(1, run_dir)

        assert result.output == "Function ran successfully"
        assert result.status is base.StepStatus.PASS

    def test_run_fail(self, run_dir):
        """Make sure stderr is captured and a non-zero return code is returned when a function assertion fails"""

        def assert_bool(arg):
            assert arg

        step = run.RunFunctionStep(assert_bool, False)
        result = step.run(1, run_dir)

        assert result.output.endswith("AssertionError: assert False\n")
        assert result.status is base.StepStatus.FAIL

    def test_run_error(self, run_dir):
        """Make sure stderr is captured and a non-zero return code is returned when a function errors out"""
        step = run.RunFunctionStep(func_to_run, True, True, kwarg1=True, kwarg2=True)
        result = step.run(1, run_dir)

        assert result.output.endswith("All args were truthy\n")
        assert result.status is base.StepStatus.ERROR

    def test_run_recursion(self, run_dir):
        """Make sure recursive functions are supported - also functions as a check for kwargs being handled properly"""
        step = run.RunFunctionStep(func_to_run, False, False, recurse_flip_flopped=True, kwarg1=False, kwarg2=False)
        result = step.run(1, run_dir)

        assert result.output.endswith("All args were truthy\n")
        assert result.status is base.StepStatus.ERROR
