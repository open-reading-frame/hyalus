"""Runs a function and then a few assertions that should error out"""
# pylint: disable=import-outside-toplevel

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__created_on__ = "2022-10-22"

from hyalus.config.steps import RunFunctionStep, AssertKeysContain
from hyalus.config.tags import Short, RegressionTest

TEST_DESCRIPTION = "Runs a function and a few assertions"
INPUT_DATA = "N/A, no input data"


def custom_func(json_file, to_dump):
    import json

    with open(json_file, 'w', encoding='utf-8') as fh:
        json.dump(to_dump, fh)


STEPS = [
    RunFunctionStep(custom_func, "output/food.json", {"best_cuisine": "Mexican"}),
    RunFunctionStep(custom_func, "output/coffee.json", {"best_coffee_shop": "Ozo"}),
    AssertKeysContain(("output/food.json", ["best_cuisine"]), "Mexican"),
]

TAGS = [Short(info="Should run in seconds"), RegressionTest("Test expected to fail until <issue> fixed")]
