"""Unit tests for the hyalus.utils.logging_utils module"""
# pylint: disable=too-few-public-methods, line-too-long

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

import logging
import re
import subprocess

import pytest

from hyalus.utils import logging_utils


@pytest.fixture(name="tmp_log")
def fixture_tmp_log(tmp_path):
    """Write a log.txt file to temp directory and return its path"""
    log_file = tmp_path / "log.txt"
    log_file.touch()
    return log_file


@pytest.fixture(name="hyalus_log_record")
def fixture_hyalus_log_record():
    """Example log record for use in formatting testing"""
    logging.setLogRecordFactory(logging_utils.HyalusLogRecord)
    record = logging.makeLogRecord(
        {
            "asctime": "2022-08-29 10:30:40,164",
            "levelname": "INFO",
            "pathname": "/path/to/root/dir/src/hyalus/some/module.py",
            "lineno": "10",
            "name": "module",
            "msg": "logging a message",
        }
    )
    logging.setLogRecordFactory(logging.LogRecord)
    return record


class TestHyalusLogRecord:
    """Unit tests for the HyalusLogRecord class"""

    def test_find_full_module(self, hyalus_log_record):
        """Test determination of the full_module attribute and that it is determined at time of init"""
        assert hyalus_log_record.full_module == __name__


class TestHyalusLogFormatter:
    """Unit tests for the HyalusLogFormatter class"""

    def test_format(self, hyalus_log_record):
        """Assert proper log formatting"""
        expected = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \[INFO\] tests.utils.test_logging_utils: \d+ - logging a message$"
        formatter = logging_utils.HyalusLogFormatter()
        assert re.match(expected, formatter.format(hyalus_log_record))


class TestConfigureLogging:
    """Unit tests for the configure_logging function. Runs in a separate interpreter session for each test."""

    def make_cmd(self, log_stdout, debug):
        """Create a command to run based on given inputs"""
        return f"""\
import logging
from hyalus.utils.logging_utils import configure_logging
configure_logging(log_stdout={log_stdout}, debug={debug})
logger = logging.getLogger()
logger.info("info message")
logger.debug("debug message")
"""

    def test_stdout_true_debug_true(self):
        """Assert when log_stdout=True and debug=True, info and debug messages are written to the log and stdout"""
        cmd = self.make_cmd(True, True)

        stdout = subprocess.check_output(["python3", "-c", cmd], text=True)
        assert "info message" in stdout and "debug message" in stdout

    def test_stdout_true_debug_false(self):
        """Assert when log_stdout=True and debug=False, only info messages are written to the log and stdout"""
        cmd = self.make_cmd(True, False)

        stdout = subprocess.check_output(["python3", "-c", cmd], text=True)
        assert "info message" in stdout and "debug message" not in stdout

    def test_stdout_false_debug_true(self):
        """Assert when log_stdout=False and debug=True, info and debug messages are written to log but not stdout"""
        cmd = self.make_cmd(False, True)

        stdout = subprocess.check_output(["python3", "-c", cmd], text=True)
        assert "info message" not in stdout and "debug message" not in stdout

    def test_stdout_false_debug_false(self):
        """Assert when log_stdout=False and debug=False, only info messages are written to log, and nothing to stdout"""
        cmd = self.make_cmd(False, False)

        stdout = subprocess.check_output(["python3", "-c", cmd], text=True)
        assert "info message" not in stdout and "debug message" not in stdout

    def test_double_call(self):
        """Assert that if configure_logging is called more than once, additional handlers are not added"""
        cmd = """\
import logging
from hyalus.utils.logging_utils import configure_logging
configure_logging(log_stdout=True)
logger = logging.getLogger()
print(len(logger.handlers))
configure_logging(log_stdout=True)
print(len(logger.handlers))
"""
        stdout = subprocess.check_output(["python3", "-c", cmd], text=True)

        assert stdout == "1\n1\n"


class TestFindHandler:
    """Tests for the find_handler utility function"""

    def test_find_handler_match(self, tmp_log):
        """Test that a Handler matching the given name is returned as expected"""
        logger = logging.getLogger()
        handler = logging_utils.HyalusFileHandler(tmp_log)
        logger.addHandler(handler)

        assert logging_utils.find_handler(str(tmp_log)) is handler

        logger.removeHandler(handler)

    def test_find_handler_no_match(self, tmp_log):
        """Test that when there are no matching Handlers found, None is returned"""
        logger = logging.getLogger()
        handler = logging_utils.HyalusFileHandler(tmp_log)
        logger.addHandler(handler)

        assert logging_utils.find_handler(str("burrito")) is None

        logger.removeHandler(handler)


class TestAddRemoveFileHandler:
    """Tests for the add_file_handler and remove_file_handler utility functions"""

    def test_add_and_remove_file_handler(self, tmp_log):
        """Assert add_file_handler properly adds a file handler and remove_file_handler removes it"""
        logger = logging.getLogger()

        # Keep track of existing Handlers that exist from running pytest
        num_handlers = len(logger.handlers)

        logging_utils.add_file_handler(tmp_log)

        assert len(logger.handlers) == num_handlers + 1
        assert str(tmp_log) in [hdlr.name for hdlr in logger.handlers]

        logging_utils.remove_file_handler(tmp_log)

        assert len(logger.handlers) == num_handlers
        assert str(tmp_log) not in [hdlr.name for hdlr in logger.handlers]

    def test_add_file_handler_already_present(self, tmp_log):
        """Assert add_file_handler short circuits if trying to add a duplicate Handler"""
        logger = logging.getLogger()

        # Keep track of existing Handlers that exist from running pytest
        num_handlers = len(logger.handlers)

        logging_utils.add_file_handler(tmp_log)
        assert len(logger.handlers) == num_handlers + 1

        logging_utils.add_file_handler(tmp_log)
        assert len(logger.handlers) == num_handlers + 1

        logging_utils.remove_file_handler(tmp_log)

    def test_remove_file_handler_not_found(self, tmp_log):
        """Assert remove_file_handler does nothing when it cannot find a Handler with the given log file"""
        logger = logging.getLogger()

        # Keep track of existing Handlers that exist from running pytest
        num_handlers = len(logger.handlers)

        logging_utils.remove_file_handler(tmp_log)
        assert len(logger.handlers) == num_handlers
