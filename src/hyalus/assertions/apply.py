"""Application of comparator functions on given values"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from typing import Any, Callable


class ConstraintApplier:
    """Apply constraint functions to given values, retrieving result values as necessary"""

    def __init__(self, func: Callable[..., bool], *args: Any) -> None:
        """Ctor.

        :param func: The function to apply
        :param args: Arguments to supply, in order, to func
        """
        self.func = func
        self.args = args

        self.__result: bool = None

    @property
    def result(self) -> bool:
        """The result of applying the given constraint function on the given arguments"""
        return self.__result

    def apply(self) -> bool:
        """Apply the function and return the result

        :return: The result of applying self.func to given arguments
        """
        if self.__result is None:
            self.__result = self.func(*self.args)

        return self.__result
