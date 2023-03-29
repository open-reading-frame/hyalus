"""Unit tests for the hyalus.utils.file_utils module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path

import pytest

from hyalus.utils import file_utils

DATA_PATH = Path(__file__).parent / "data"


class TestGlobFile:
    """Unit tests for the glob_file utility function"""

    def test_glob_file_pass(self):
        """Test globbing for wildcard file path in case where 1 result will be found"""
        assert file_utils.glob_file(DATA_PATH / "*.tsv") == DATA_PATH / "example.tsv"

    def test_glob_file_not_found(self):
        """Assert InvalidWildcard is raised when giving a wildcard that cannot be found"""
        with pytest.raises(file_utils.InvalidWildcard):
            file_utils.glob_file(DATA_PATH / "*.not_a_ext")

    def test_glob_file_multiple_found(self):
        """Assert InvalidWildcard is raised from giving a wildcard with multiple results"""
        with pytest.raises(file_utils.InvalidWildcard):
            file_utils.glob_file(DATA_PATH / "*sv")
