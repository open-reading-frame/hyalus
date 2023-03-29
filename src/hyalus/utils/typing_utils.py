"""Utilities related to typing and type casting values"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from types import GenericAlias
from typing import Any, get_origin, get_args


def type_string(string: str) -> int | float | bool | str:
    """Given a string, try type casting to int/float/bool accordingly

    :param string: The string to type cast
    :return: The type-casted value
    """
    try:
        return int(string)
    except ValueError:
        pass

    try:
        return float(string)
    except ValueError:
        pass

    if string.lower() == "true":
        return True
    if string.lower() == "false":
        return False

    return string


def type_check(item: Any, item_type: type | GenericAlias) -> bool:
    """Checks if the given item is an instance of the given type. Mostly a wrapper around the builtin isinstance with
    support for type checking against generics in which the class is either list, set, tuple, or dict

    :param item: The item to type check
    :param item_type: The type to check against
    :return: True if the item matches the given type
    :raises ValueError: If given a generic type that is unknown
    """
    # Short circuit when not given GenericAlias since isinstance should be able to handle most other types
    if not isinstance(item_type, GenericAlias):
        return isinstance(item, item_type)

    # get_origin gets the container type class, e.g. list in list[int]
    if not isinstance(item, get_origin(item_type)):
        return False

    # Checking for empty container - no items to check against the item_type's args
    if not item:
        return False

    if isinstance(item, (list, set)):
        return all(type_check(i, get_args(item_type)[0]) for i in item)

    if isinstance(item, tuple):
        return all(type_check(i, t) for i, t in zip(item, get_args(item_type)))

    if isinstance(item, dict):
        key_type, value_type = get_args(item_type)
        return all(type_check(k, key_type) and type_check(v, value_type) for k, v in item.items())

    raise ValueError(f"Could not type check against type: {item_type}")
