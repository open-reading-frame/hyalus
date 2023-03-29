"""JSON-related utilities"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import logging
from typing import Sequence, TypeAlias

_logger = logging.getLogger("hyalus.utils.json_utils")

# Custom types
#: Type representing possible literals for JSON values
JSONLiteral: TypeAlias = str | int | float | bool | None

#: Type representing possible JSON structure types
JSONObject: TypeAlias = dict | list

#: Type representing possible values within an object or array in JSON
JSONValue: TypeAlias = JSONObject | JSONLiteral


def json_get(obj: JSONObject, path_list: Sequence[str | int]) -> JSONValue:
    """Given a JSON object and list of keys/indices, retrieve a value

    :param obj: The JSON object to inspect
    :param path_list: The list of keys/indices for inspection of the given object
    :return: The retrieved value
    :raises KeyError: If a given key in path_list was not found
    :raises IndexError: If a given index in path_list was not found
    """
    for key_or_index in path_list:
        obj = obj[key_or_index]  # type: ignore[index]

    return obj


def json_set(obj: JSONObject, path_list: Sequence[str | int], value: JSONValue, create_key: bool = False) -> None:
    """Given a JSON object, list of keys/indices, and value, set the given value at the given location in the object

    :param obj: The JSON object to update
    :param path_list: The list of keys/indices corresponding to the location to update in the object
    :param value: The value to set at the given location
    :param create_key: Boolean specifying whether to create a key with the given value if the key is not already present
    :raises KeyError: If a given key in path_list was not found
    :raises IndexError: If a given index in path_list was not found
    :raises ValueError: If the given path_list is empty
    """
    if not path_list:
        raise ValueError("Need at least 1 key/index in the path list to set value")

    to_set = json_get(obj, path_list[:-1])

    if isinstance(to_set, dict) and path_list[-1] not in to_set and not create_key:
        raise KeyError(f"create_key set to False and did not find key {path_list[-1]} to update")

    to_set[path_list[-1]] = value  # type: ignore[index]


def json_append(obj: JSONObject, path_list: Sequence[str | int], value: JSONValue) -> None:
    """Given a JSON object, list of keys/indices, and value, append the given value at the given location in the object

    :param obj: The JSON object to update
    :param path_list: The list of keys/indices corresponding to the location to update in the object
    :param value: The value to append at the given location
    :raises KeyError: If a given key in path_list was not found
    :raises IndexError: If a given index in path_list was not found
    :raises ValueError: If the path_list leads to something other than a list
    """
    append_to = json_get(obj, path_list)

    try:
        append_to.append(value)  # type: ignore[union-attr]
    except AttributeError as exc:
        raise ValueError(f"Did not find list at given path {path_list} to append to") from exc
