"""Example config file which has fields with values of an invalid type"""

__author__ = 1
__credits__ = []
__created_on__ = 4

from hyalus.config.steps.run import RunFunctionStep
from hyalus.config.tags.runtime import Short

TEST_DESCRIPTION = 3
INPUT_DATA = None


def custom_func(value):
    if not value:
        raise Exception("value was false or empty")


STEPS = {Short(info="Should run in seconds")}

TAGS = [
    RunFunctionStep(custom_func, True),
    RunFunctionStep(custom_func, [1]),
]
