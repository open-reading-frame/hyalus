"""Utilities related to logging"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import inspect
import logging
import os.path
from pathlib import Path
import sys
from typing import TextIO


class HyalusLogRecord(logging.LogRecord):
    """A LogRecord that also stores the __name__ attribute of the module from which the logging call was made"""

    # pylint: disable=too-many-arguments
    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func=None, sinfo=None, **kwargs):
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func=func, sinfo=sinfo, **kwargs)

        self.full_module = self.find_full_module()

    def find_full_module(self):
        """Find the stack frame of the logging call to get the __name__ attribute from the module the call lives in."""
        frame = inspect.currentframe()

        # Copied from logging based on a workaround to handle IronPython - should not matter here but just to be safe...
        if frame is None:  # pragma: no cover
            return self.module

        # Search the stack until we find a function that wasn't defined in this module or the logging module
        while hasattr(frame, "f_code"):
            filename = os.path.normcase(frame.f_code.co_filename)

            if filename in {logging.__file__, __file__}:
                frame = frame.f_back
                continue

            break

        return frame.f_globals["__name__"]


class HyalusLogFormatter(logging.Formatter):
    """Custom log formatter which will take the pathname attribute and create a module_path attribute accordingly"""

    def __init__(self):
        super().__init__("%(asctime)s [%(levelname)s] %(full_module)s: %(lineno)s - %(msg)s")


class HyalusFileHandler(logging.FileHandler):
    """Custom FileHandler that uses the HyalusLogFormatter for formatting"""

    def __init__(self, log_file: str | Path) -> None:
        """Ctor.

        :param log_file: The path to the log file for the handler
        """
        super().__init__(log_file, mode='a')
        self.setFormatter(HyalusLogFormatter())
        self.set_name(str(log_file))


class HyalusStreamHandler(logging.StreamHandler):
    """Custom StreamHandler that uses the HyalusLogFormatter for formatting"""

    def __init__(self, stream: TextIO) -> None:
        """Ctor.

        :param stream: The IO stream object to write to
        """
        super().__init__(stream)
        self.setFormatter(HyalusLogFormatter())
        self.set_name(stream.name)


def configure_logging(log_stdout: bool = False, debug: bool = False) -> None:
    """Configure logging for hyalus - should only be called once per interpreter session. Will short circuit otherwise.

    :param log_file: Path to the log_file for the run
    :param log_stdout: Boolean flag for logging messages to stdout
    :param debug: Boolean flag to set the logging level to DEBUG (default is INFO)
    """
    # Change the LogRecord used so that the full_module attribute is populated and can be used
    logging.setLogRecordFactory(HyalusLogRecord)

    root_logger = logging.getLogger()

    if root_logger.hasHandlers():
        return

    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    if log_stdout:
        root_logger.addHandler(HyalusStreamHandler(sys.stdout))


def find_handler(name: str, logger: logging.Logger = None) -> logging.Handler | None:
    """Finds the first instance of a Handler with the given name. Returns None if one cannot be found.

    :param name: The name of the Handler
    :param logger: The logger to inspect. If none given, the root logger is used.
    :return: The corresponding Handler, if any exist, or else None
    """
    if not logger:
        logger = logging.getLogger()

    for handler in logger.handlers:
        if handler.name == name:
            return handler

    return None


def add_file_handler(log_file: Path | str, logger: logging.Logger = None) -> None:
    """Given a log file path, create a handler and add it to the root logger

    :param log_file: The log file path
    :param logger: The logger to update. If none given, the root logger is used.
    """
    if not logger:
        logger = logging.getLogger()

    if handler := find_handler(str(log_file), logger=logger):
        logger.addHandler(handler)
    else:
        logger.addHandler(HyalusFileHandler(log_file))


def remove_file_handler(log_file: Path | str, logger: logging.Logger = None) -> None:
    """Given a log file path, find the corresponding handler if it exists and remove it. If not found, return.

    :param log_file: The log file path
    :param logger: The logger to inspect. If none given, the root logger is used.
    """
    if not logger:
        logger = logging.getLogger()

    if handler := find_handler(str(log_file), logger=logger):
        logger.removeHandler(handler)
