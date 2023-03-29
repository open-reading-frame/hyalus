"""Example valid config file"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__created_on__ = "2022-09-22"

from hyalus.config.steps.run import RunFunctionStep
from hyalus.config.tags.runtime import Short

TEST_DESCRIPTION = "Runs a function and calls it a day"
INPUT_DATA = "N/A, no input data"


def custom_func(value):
    if not value:
        raise Exception("value was false or empty")


STEPS = [
    RunFunctionStep(custom_func, True),
    RunFunctionStep(custom_func, [1]),
]

TAGS = [Short(info="Should run in seconds")]
