"""Functionality related to running hyalus Steps in the context of python functions and/or pytest"""
# pylint: disable=invalid-name

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from functools import wraps
import inspect
from pathlib import Path
import shutil
import tempfile
import types
from typing import Callable, TypeVar, Type, Any

try:
    import pytest
except ImportError:  # pragma: no cover
    pytest = None

from hyalus.config.steps.base import StepBase
from hyalus.run.common import make_run_dir

RUN_DIR = "run_dir"

DecoratorType = Callable[[Callable], Callable]
T_cls = TypeVar("T_cls", bound=type)
T_decorator = TypeVar("T_decorator", bound=DecoratorType | Type[staticmethod | classmethod])
T_decoratee = TypeVar("T_decoratee", bound=Callable[..., Any] | staticmethod | classmethod)


def apply_decorator(decorator: T_decorator) -> Callable[[T_cls], T_cls]:
    """Decorator that applies a given decorator to all defined methods of a class. For example:

    ::

        @apply_decorator(staticmethod)
        class MyClass:

            @pytest.fixture(name="my_fixture")
            def fixture_my_fixture():
                ...

            def method_1():
                ...

            def method_2():
                ...

    is roughly equivalent to

    ::

        class MyClass:

            @staticmethod
            @pytest.fixture(name="my_fixture")
            def fixture_my_fixture():
                ...

            @staticmethod
            def method_1():
                ...

            @staticmethod
            def method_2():
                ...

    This allows you to systematically run functionality at the start of each test within a test class with a bit more
    flexibility than what pytest fixtures give (can send in parameters to the decorator) and in a single line rather
    than updating each test method's signature to request a fixture

    :param decorator: The decorator to decorate all methods with
    :return: Function that decorates a given class' methods with the given decorator
    """

    def decorate_cls(cls: T_cls) -> T_cls:
        """Decorate the class by updating each method with the decorator

        :param cls: The class to decorate
        :return: The decorated class
        """
        for name, member in vars(cls).items():
            if callable(member):
                setattr(cls, name, decorator(member))

        return cls

    return decorate_cls


if pytest is not None:

    @pytest.fixture(name=RUN_DIR)
    def fixture_run_dir(tmp_path):
        """Fixture that wraps tmp_path, creating relevant hyalus run subdirectories

        .. note:: Only defined if pytest is installed - won't be used in any other instance anyway
        """
        return make_run_dir(tmp_path)


def run_steps(*steps: StepBase, running_pytest: bool = True, temp_dir: str | Path = None) -> DecoratorType:
    r"""Decorator that will create a temp directory if needed and run given Steps prior to execution of a function.
    For example:

    ::

        @run_steps(ExampleStep(1, 2), ExampleStep(3, 4), running_pytest=False)
        def three_input_sum(a, b, c):
            return a + b + c

    would be roughly equivalent to:

    ::

        def three_input_sum(a, b, c):
            ExampleStep(1, 2).run(1, "<some_temp_dir_path>")
            ExampleStep(3, 4).run(2, "<some_temp_dir_path>")
            return a + b + c

    When used in the context of a pytest-style test, the ``run_dir`` fixture (defined in this module) is used instead
    of an arbitrary temp directory:

    ::

        @run_steps(ExampleStep(1, 2), ExampleStep(3, 4), running_pytest=True))
        def test_something(run_dir):
            my_condition = some_module.function_call(run_dir)

            assert my_condition

    would be roughly equivalent to:

    ::

        def test_something(run_dir):
            ExampleStep(1, 2).run(1, run_dir)
            ExampleStep(3, 4).run(2, run_dir)
            my_condition = some_module.function_call(run_dir)

            assert my_condition

    The test function does not need to specify the ``run_dir`` fixture. The decorator will act like the fixture is
    present either way when ``running_pytest`` is set to ``True``. For example:

    ::

        @run_steps(ExampleStep(1, 2), ExampleStep(3, 4), running_pytest=True))
        def test_something():
            my_condition = some_module.function_call(True, False, True)

            assert my_condition

    would be roughly equivalent to (note the addition of ``run_dir`` as a fixture):

    ::

        def test_something(run_dir):
            ExampleStep(1, 2).run(1, run_dir)
            ExampleStep(3, 4).run(2, run_dir)
            my_condition = some_module.function_call(True, False, True)

            assert my_condition

    .. note:: Scope still applies and if ``run_dir`` is not originally in the function's signature, it may not be
        directly used by the code originally defined within the decorated function

    :py:func:`run_steps` can also be used with the :py:func:`apply_decorator` class decorator to apply the given Step
    execution prior to all defined tests under a test class. When used in this fashion as well as with a constituent
    method of the class, the class-decoration-level steps are run prior to method-decoration-level steps.

    :param \*steps: Steps to run prior to function execution
    :param running_pytest: Flag that tells the decorator whether the function is expected to be executed via pytest.
        When set to True, the ``run_dir`` fixture will be used and the function will be decorated in a way that pytest
        can handle.
    :param temp_dir: Use the given temp directory to run Steps in - not used if ``running_pytest`` is ``True``
    :return: The function decorator
    """

    def decorate(fn: T_decoratee) -> T_decoratee:
        # If the given "function" is actually a staticmethod/classmethod object, get the function itself
        encapsulating_decorator: Type[staticmethod | classmethod] = None
        to_decorate: Callable[..., Any] = None

        if isinstance(fn, types.FunctionType):
            to_decorate = fn

        if isinstance(fn, (staticmethod, classmethod)):
            encapsulating_decorator = type(fn)
            to_decorate = fn.__func__

        signature = inspect.signature(to_decorate)
        params = signature.parameters

        # NOTE: Under this path it is assumed that the caller of the function being decorated is going to be pytest.
        # pytest takes fixtures for test functions/methods and converts them to keyword arguments at run time based on
        # the names of the fixtures being used
        if running_pytest:
            # Change the function's signature to include the run_dir fixture so that pytest thinks it was requested
            # Note that this does not actually change what the function expects when being called!
            if add_run_dir := RUN_DIR not in params:
                positional_args = [param for param in params.values() if param.default == inspect.Parameter.empty]
                keyword_args = [param for param in params.values() if param.default != inspect.Parameter.empty]
                positional_args.append(inspect.Parameter(RUN_DIR, inspect.Parameter.POSITIONAL_OR_KEYWORD))
                to_replace = tuple(positional_args + keyword_args)
                to_decorate.__signature__ = signature.replace(parameters=to_replace)  # type: ignore[attr-defined]

            @wraps(to_decorate)
            def wrapper(*args, **kwargs):
                for i, step in enumerate(steps, start=1):
                    step.run(i, kwargs[RUN_DIR])

                # If we changed the inspected signature to include run_dir, remove it before calling the test function
                # itself because the actual signature did not include it
                if add_run_dir:
                    kwargs.pop(RUN_DIR)

                # pytest still calls the test function itself with arguments as positional arguments, take **kwargs
                # values and send them in as positional arguments after non-fixture positional arguments e.g. self
                return to_decorate(*args, *kwargs.values())

        else:

            @wraps(to_decorate)
            def wrapper(*args, **kwargs):
                # Create an arbitrary temp directory to run Steps in if one was not passed in
                run_dir = make_run_dir(temp_dir) if temp_dir else make_run_dir(tempfile.mkdtemp())

                for i, step in enumerate(steps, start=1):
                    step.run(i, run_dir)

                # Capture output from running the function before cleaning up the temp directory
                output = to_decorate(*args, **kwargs)

                # Clean up the created temp directory if one was not passed in
                if not temp_dir:
                    shutil.rmtree(run_dir)

                return output

        # Re-wrap the decorated function in the original encapsulating decorator if needed - mypy is confused here
        return encapsulating_decorator(wrapper) if encapsulating_decorator else wrapper  # type: ignore[return-value]

    return decorate
