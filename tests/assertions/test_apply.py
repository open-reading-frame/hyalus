"""Unit tests for the hyalus.assertions.apply module"""
# pylint: disable=too-few-public-methods

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from hyalus.assertions import apply, compare


def ge_multi(arg1, arg2, arg3):
    """In-order check of greater than or equal to, using positional args"""
    return arg1 >= arg2 >= arg3


class TestConstraintApplier:
    """Unit tests for the ConstraintApplier class"""

    def test_apply_two_args_1(self):
        """Test the apply method with two positional arguments, True result"""
        applier = apply.ConstraintApplier(compare.ge, 4, 4)
        assert applier.apply() is True
        assert applier.result is True

    def test_apply_two_args_2(self):
        """Test the apply method with two positional arguments, False result"""
        applier = apply.ConstraintApplier(compare.ge, 4, 5)
        assert applier.apply() is False
        assert applier.result is False

    def test_apply_three_args_1(self):
        """Test the apply method with three positional arguments, True result"""
        applier = apply.ConstraintApplier(ge_multi, 6, 5, 4)
        assert applier.apply() is True
        assert applier.result is True

    def test_apply_three_args_2(self):
        """Test the apply method with three positional arguments, False result"""
        applier = apply.ConstraintApplier(ge_multi, 6, 7, 4)
        assert applier.apply() is False
        assert applier.result is False
