"""Utilities for handling pandas objects"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from typing import Any, Sequence

try:
    import pandas as pd
except ImportError:
    pd = None


def subset_dataframe(df: pd.DataFrame, constraints: Sequence[tuple[str, Any]]) -> pd.DataFrame:
    """Given a list of constraints, subset the given ``DataFrame`` to records matching all of the constraints

    :param df: The ``DataFrame`` to subset
    :param constraints: The list of pairs of (column, value) constraints to apply
    :return: The subset of records in the ``DataFrame`` matching given constraints
    """
    for constraint in constraints:
        column, value = constraint

        df = df[df[column] == value]

    return df
