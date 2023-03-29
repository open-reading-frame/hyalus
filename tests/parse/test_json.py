"""Unit tests for the hyalus.parse.json module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path
import shutil

import pytest

import hyalus.parse.json as json_parse

DATA_PATH = Path(__file__).parent / "data"
JSON_1 = DATA_PATH / "example_1.json"
JSON_2 = DATA_PATH / "example_2.json"


@pytest.fixture(name="tmp_json")
def fixture_tmp_json(tmp_path):
    """Copies JSON_1 file to a temp directory and returns path to the file"""
    shutil.copy2(JSON_1, tmp_path)
    return tmp_path / "example_1.json"


class TestJSONParser:
    """Unit tests for the JSONParser class"""

    def test_eq_true_file_path(self):
        """Assert that two parsers with the same file path are treated as equal"""
        assert json_parse.JSONParser("path/to/file.json") == json_parse.JSONParser("path/to/file.json")

    def test_eq_true_parse(self, tmp_json):
        """Assert that two parsers with different file paths but the same parsed content are treated as equal"""
        assert json_parse.JSONParser(tmp_json) == json_parse.JSONParser(JSON_1)

    def test_eq_false(self):
        """Assert that two parsers with different file paths and different content are treated as unequal"""
        assert json_parse.JSONParser(JSON_1) != json_parse.JSONParser(JSON_2)

    def test_search_single_key(self):
        """Test searching through a JSON file when giving a single key"""
        assert json_parse.JSONParser(JSON_1).search("key1") == [0, 1, 2, 3]

    def test_search_multiple_key(self):
        """Test searching through a JSON file when giving a single key"""
        assert json_parse.JSONParser(JSON_1).search(["key2", "a", 0]) == 1
