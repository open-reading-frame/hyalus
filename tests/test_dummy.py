"""Tests for the action_utils.common module"""

__author__ = "Your name here"

import pytest


@pytest.fixture(name="some_expected_string")
def fixture_some_expected_string():
    return "EXPECTED"


class TestStringComp:
    """Dummy tests"""

    @staticmethod
    def test_string_match(some_expected_string):
        """Assert strings match"""
        assert some_expected_string == "EXPECTED"

    @staticmethod
    def test_string_mismatch(some_expected_string):
        """Assert strings don't match"""
        assert some_expected_string != "NOT EXPECTED"
