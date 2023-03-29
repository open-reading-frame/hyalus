"""Utilities related to handling file paths/handles"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from glob import glob
from pathlib import Path


class InvalidWildcard(Exception):
    """Exception used to represent a wildcard that could not be used to find a single file"""


def glob_file(wildcard: str | Path) -> Path:
    """Glob for a given wildcard file path and return the result, if and only if 1 result is found.

    :param wildcard: The wildcard to glob
    :return: The globbed file path
    :raises InvalidWildcard: If the given wildcard did not result in a file being found, or resulted in multiple
        being found
    """
    result = glob(str(wildcard))

    if not result:
        raise InvalidWildcard(f"Wildcard {wildcard} could not be found")

    if len(result) > 1:
        raise InvalidWildcard(f"Wildcard {wildcard} expanded into more than one result:\n\n{', '.join(result)}")

    return Path(result[0])
