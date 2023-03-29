"""Tests for the hyalus.run.python module"""
# pylint: disable=no-method-argument, no-self-argument, protected-access, too-few-public-methods, missing-class-docstring

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
import shutil
import tempfile
import types
from typing import Any

from hyalus.config import common
from hyalus.config.steps import base
from hyalus.run import python


# pylint: disable=missing-function-docstring
@python.apply_decorator(staticmethod)
class ToDecorate:
    """Example class with methods being decorated as staticmethods using the apply_decorator decorator"""

    def some_method():
        return True

    def some_other_method():
        return False

    def yet_another_method():
        return "burrito"


class TestApplyDecorator:
    """Tests specific to the apply_decorator class decorator"""

    @staticmethod
    def test_decorator_applied():
        """Verify all methods for a class decorated with apply_decorator(staticmethod) are static"""
        assert isinstance(ToDecorate().some_method, types.FunctionType)
        assert isinstance(ToDecorate().some_other_method, types.FunctionType)
        assert isinstance(ToDecorate().yet_another_method, types.FunctionType)


class ValueWriter(base.StepBase):
    """Dummy Step for used in testing of run_steps decorator"""

    def __init__(self, to_write: Any, file_path: str | Path = None) -> None:
        """Ctor.

        :param to_write: Value to write to file
        :param file_path: Override the file_path writing to write to this file instead of the hyalus dir
        """
        self.to_write = str(to_write)
        self.file_path = file_path

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.to_write}, {self.file_path})"

    @property
    def needs(self):
        return []

    def _run_workflow(self, pre_process_output: Any = None) -> base.StepOutput:
        """Run the Step's workflow

        :param pre_process_output: Output from pre-processing
        :return: Output from running the workflow to pass to _post_process
        """
        if self.file_path:
            file_path = Path(self.file_path)
        else:
            file_path = self.run_dir / common.HYALUS_PATH / f"Step_{self.step_number}.txt"

        try:
            with open(file_path, 'w', encoding="utf-8") as fh:
                fh.write(self.to_write)
        except Exception:  # pylint: disable=broad-except
            return base.StepOutput(None, base.StepStatus.FAIL)

        return base.StepOutput(file_path, base.StepStatus.PASS)


@python.apply_decorator(staticmethod)
class TestRunSteps:
    """Tests for the run_steps decorator when decorating functions that are not executed by pytest"""

    def test_run_steps_no_tempdir():
        """Assert the run_steps decorator can handle creating a temp dir, running steps in it, and tearing it down"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as output_file:

            @python.run_steps(ValueWriter("burrito", file_path=output_file.name), running_pytest=False)
            def fn_no_tempdir():
                with open(output_file.name, 'r', encoding="utf-8") as fh:
                    return fh.read() == "burrito"

            assert fn_no_tempdir()

    def test_run_steps_str_tempdir():
        """Assert the run_steps decorator can handle running in a given temp_dir that is a string"""
        str_temp_dir = tempfile.mkdtemp()

        @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=str_temp_dir)
        def fn_str_temp_dir():
            """Inspects files written by run_steps and confirms they have expected content"""
            check_1 = Path(str_temp_dir) / common.HYALUS_PATH / "Step_1.txt"
            check_2 = Path(str_temp_dir) / common.HYALUS_PATH / "Step_2.txt"

            with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert fn_str_temp_dir()
        assert Path(str_temp_dir).is_dir()
        shutil.rmtree(str_temp_dir)

    def test_run_steps_path_tempdir():
        """Assert the run_steps decorator can handle running in a given temp_dir that is a Path object"""
        path_temp_dir = Path(tempfile.mkdtemp())

        @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=path_temp_dir)
        def fn_path_temp_dir():
            """Inspects files written by run_steps and confirms they have expected content"""
            check_1 = path_temp_dir / common.HYALUS_PATH / "Step_1.txt"
            check_2 = path_temp_dir / common.HYALUS_PATH / "Step_2.txt"

            with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert fn_path_temp_dir()
        assert path_temp_dir.is_dir()
        shutil.rmtree(path_temp_dir)

    def test_run_steps_method_decoration():
        """Assert that run_steps can decorate a method"""
        temp_dir = Path(tempfile.mkdtemp())

        class Container:
            @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=temp_dir)
            def fn_path_temp_dir(self):
                """Inspects files written by run_steps and confirms they have expected content"""
                check_1 = temp_dir / common.HYALUS_PATH / "Step_1.txt"
                check_2 = temp_dir / common.HYALUS_PATH / "Step_2.txt"

                with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                    return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert Container().fn_path_temp_dir()
        assert temp_dir.is_dir()
        shutil.rmtree(temp_dir)

    def test_run_steps_staticmethod_decoration():
        """Assert that run_steps can decorate a staticmethod"""
        temp_dir = Path(tempfile.mkdtemp())

        class Container:
            @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=temp_dir)
            @staticmethod
            def fn_path_temp_dir():
                """Inspects files written by run_steps and confirms they have expected content"""
                check_1 = temp_dir / common.HYALUS_PATH / "Step_1.txt"
                check_2 = temp_dir / common.HYALUS_PATH / "Step_2.txt"

                with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                    return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert Container().fn_path_temp_dir()
        assert temp_dir.is_dir()
        shutil.rmtree(temp_dir)

    def test_run_steps_decoration_by_staticmethod():
        """Assert that the resulting function coming out of run_steps can be decorated by staticmethod"""
        temp_dir = Path(tempfile.mkdtemp())

        class Container:
            @staticmethod
            @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=temp_dir)
            def fn_path_temp_dir():
                """Inspects files written by run_steps and confirms they have expected content"""
                check_1 = temp_dir / common.HYALUS_PATH / "Step_1.txt"
                check_2 = temp_dir / common.HYALUS_PATH / "Step_2.txt"

                with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                    return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert Container().fn_path_temp_dir()
        assert temp_dir.is_dir()
        shutil.rmtree(temp_dir)

    def test_run_steps_classmethod_decoration():
        """Assert that run_steps can decorate a classmethod"""
        temp_dir = Path(tempfile.mkdtemp())

        class Container:
            @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=temp_dir)
            @classmethod
            def fn_path_temp_dir(cls):
                """Inspects files written by run_steps and confirms they have expected content"""
                check_1 = temp_dir / common.HYALUS_PATH / "Step_1.txt"
                check_2 = temp_dir / common.HYALUS_PATH / "Step_2.txt"

                with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                    return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert Container.fn_path_temp_dir()
        assert Container().fn_path_temp_dir()
        assert temp_dir.is_dir()
        shutil.rmtree(temp_dir)

    def test_run_steps_decoration_by_classmethod():
        """Assert that the resulting function coming out of run_steps can be decorated by classmethod"""
        temp_dir = Path(tempfile.mkdtemp())

        class Container:
            @classmethod
            @python.run_steps(ValueWriter("burrito"), ValueWriter("taco"), running_pytest=False, temp_dir=temp_dir)
            def fn_path_temp_dir(cls):
                """Inspects files written by run_steps and confirms they have expected content"""
                check_1 = temp_dir / common.HYALUS_PATH / "Step_1.txt"
                check_2 = temp_dir / common.HYALUS_PATH / "Step_2.txt"

                with open(check_1, 'r', encoding="utf-8") as fh_1, open(check_2, 'r', encoding="utf-8") as fh_2:
                    return fh_1.read() == "burrito" and fh_2.read() == "taco"

        assert Container.fn_path_temp_dir()
        assert Container().fn_path_temp_dir()
        assert temp_dir.is_dir()
        shutil.rmtree(temp_dir)

    def test_run_steps_apply_decorator():
        """Make sure that run_steps correctly decorates methods when used by the apply_decorator class decorator"""
        temp_dir = Path(tempfile.mkdtemp())

        @python.apply_decorator(python.run_steps(ValueWriter("taco"), running_pytest=False, temp_dir=temp_dir))
        class ApplyRunStepsDecorator:
            def fn_path_temp_dir_1(self):
                """Inspects files written by run_steps and confirms they have expected content"""
                to_check = temp_dir / common.HYALUS_PATH / "Step_1.txt"

                with open(to_check, 'r', encoding="utf-8") as fh:
                    return fh.read() == "taco"

            def fn_path_temp_dir_2(self):
                """Inspects files written by run_steps and confirms they have expected content"""
                to_check = temp_dir / common.HYALUS_PATH / "Step_1.txt"

                with open(to_check, 'r', encoding="utf-8") as fh:
                    return fh.read() == "taco"

        assert ApplyRunStepsDecorator().fn_path_temp_dir_1()
        assert ApplyRunStepsDecorator().fn_path_temp_dir_2()
        assert temp_dir.is_dir()
        shutil.rmtree(temp_dir)


@python.run_steps(ValueWriter("burrito"))
def test_run_steps_test_function_with_run_dir_fixture(run_dir):
    """Tests that a function being run by pytest that uses the run_dir fixture is decorated as expected"""
    to_check = run_dir / common.HYALUS_PATH / "Step_1.txt"

    with open(to_check, 'r', encoding="utf-8") as fh:
        assert fh.read() == "burrito"


@python.run_steps(ValueWriter("burrito"))
def test_run_steps_test_function_without_run_dir_fixture(tmp_path):
    """Tests that a function being run by pytest that does not use the run_dir fixture is decorated as expected"""
    to_check = tmp_path / common.HYALUS_PATH / "Step_1.txt"

    with open(to_check, 'r', encoding="utf-8") as fh:
        assert fh.read() == "burrito"


class TestPytestRunSteps:
    """Testing for test methods/staticmethods being decorated by run_steps"""

    @python.run_steps(ValueWriter("burrito"))
    def test_run_steps_method_with_run_dir_fixture(self, run_dir):
        """Tests that a method being run by pytest that uses the run_dir fixture is decorated as expected"""
        to_check = run_dir / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"

    @python.run_steps(ValueWriter("burrito"))
    def test_run_steps_method_without_run_dir_fixture(self, tmp_path):
        """Tests that a method being run by pytest that does not use the run_dir fixture is decorated as expected"""
        to_check = tmp_path / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"

    @python.run_steps(ValueWriter("burrito"))
    @staticmethod
    def test_run_steps_staticmethod_with_run_dir_fixture(run_dir):
        """Tests that a staticmethod being run by pytest that uses the run_dir fixture is correctly decorated"""
        to_check = run_dir / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"

    @python.run_steps(ValueWriter("burrito"))
    @staticmethod
    def test_run_steps_staticmethod_without_run_dir_fixture(tmp_path):
        """Tests that a staticmethod being run by pytest that does not use the run_dir fixture is correctly decorated"""
        to_check = tmp_path / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"

    @staticmethod
    @python.run_steps(ValueWriter("burrito"))
    def test_run_steps_with_run_dir_fixture_decorated_by_staticmethod(run_dir):
        """Tests that staticmethod can decorate a method being run by pytest uses the run_dir fixture"""
        to_check = run_dir / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"

    @staticmethod
    @python.run_steps(ValueWriter("burrito"))
    def test_run_steps_without_run_dir_fixture_decorated_by_staticmethod(tmp_path):
        """Tests that staticmethod can decorate a method being run by pytest that does not use the run_dir fixture"""
        to_check = tmp_path / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"


@python.apply_decorator(staticmethod)
@python.apply_decorator(python.run_steps(ValueWriter("burrito")))
class TestPytestApplyDecoratorRunSteps:
    """Make sure that run_steps can be used with apply_decorator in the context of a pytest test class"""

    def test_example_1(run_dir):
        to_check = run_dir / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"

    def test_example_2(tmp_path):
        to_check = tmp_path / common.HYALUS_PATH / "Step_1.txt"

        with open(to_check, 'r', encoding="utf-8") as fh:
            assert fh.read() == "burrito"
