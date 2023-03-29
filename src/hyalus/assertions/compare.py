"""Comparator functions for expected and observed values. Expected to be used in the context of an assertion."""
# pylint: disable=invalid-name

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from typing import Any, Hashable

try:
    import pandas as pd
except ImportError:
    pd = None

from hyalus.utils.pandas_utils import subset_dataframe


def eq(*args: Any) -> bool:
    """Boolean check for whether the given values are all equal to each other

    :param args: Values, in order, for the comparison
    :return: True if all values are equal, otherwise False
    """
    if not args:
        return True

    return args.count(args[0]) == len(args)


def ne(*args: Any) -> bool:
    """Boolean check for whether the given values are all unequal to each other - no 2 values may be equal

    :param args: Values, in order, for the comparison
    :return: True if no values are equal, otherwise False
    """
    for i, value in enumerate(args, start=1):
        if value in args[i:]:
            return False

    return True


def gt(*args: Any) -> bool:
    """Boolean check for whether the given values are, in order, greater than the next value

    :param args: Values, in order, for the comparison
    :return: True if values are, in order, greater than the next value
    """
    for index, item in enumerate(args[:-1]):
        if item <= args[index + 1]:
            return False

    return True


def ge(*args: Any) -> bool:
    """Boolean check for whether the given values are, in order, greater than or equal to the next value

    :param args: Values, in order, for the comparison
    :return: True if values are, in order, greater than or equal to the next value
    """
    for index, item in enumerate(args[:-1]):
        if item < args[index + 1]:
            return False

    return True


def lt(*args: Any) -> bool:
    """Boolean check for whether the given values are, in order, less than the next value

    :param args: Values, in order, for the comparison
    :return: True if values are, in order, less than the next value
    """
    for index, item in enumerate(args[:-1]):
        if item >= args[index + 1]:
            return False

    return True


def le(*args: Any) -> bool:
    """Boolean check for whether the given values are, in order, less than or equal to the next value

    :param args: Values, in order, for the comparison
    :return: True if values are, in order, less than or the next value
    """
    for index, item in enumerate(args[:-1]):
        if item > args[index + 1]:
            return False

    return True


def is_(*args: Any) -> bool:
    """Boolean check for whether all of the given values are identical to each other (via identity)

    :param args: Values, in order, for the comparison
    :return: True if all values are identical (via identity), otherwise False
    """
    if not args:
        return True

    all_values = [id(value) for value in args]

    return all_values.count(all_values[0]) == len(all_values)


def is_not(*args: Any) -> bool:
    """Boolean check for whether none of the given values are identical to each other (via identity)

    :param args: Values, in order, for the comparison
    :return: True if any values are identical (via identity), otherwise False
    """
    all_values = [id(value) for value in args]

    return len(all_values) == len(set(all_values))


def in_(a: Any, b: Any) -> bool:
    """Return the outcome of the test ``a in b``"""
    return a in b


def not_in(a: Any, b: Any) -> bool:
    """Return the outcome of the test ``a not in b``"""
    return a not in b


def contains(a: Any, b: Any) -> bool:
    """Return the outcome of the test ``b in a``"""
    return b in a


def does_not_contain(a: Any, b: Any) -> bool:
    """Return the outcome of the test ``b not in a``"""
    return b not in a


def keys_contain(a: dict, b: Hashable) -> bool:
    """Return the outcome of the test ``b in a.keys()``"""
    return b in a.keys()


def values_contain(a: dict, b: Any) -> bool:
    """Return the outcome of the test ``b in a.values()``"""
    return b in a.values()


def items_contain(a: dict, b: tuple[Hashable, Any]) -> bool:
    """Return the outcome of the test ``b in a.items()``"""
    return b in a.items()


def dataframe_contains(a: pd.DataFrame, b: tuple[str, Any] | list[tuple[str, Any]]) -> bool:
    """Return True if at least one record in the given DataFrame matches all given pairs of column/value, else False"""
    if isinstance(b, tuple):
        b = [b]

    return not subset_dataframe(a, b).empty
