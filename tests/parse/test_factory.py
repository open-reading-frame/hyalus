"""Unit tests for the hyalus.parse.factory module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path

from hyalus.parse import factory, csv, json as json_parse, tsv

DATA_PATH = Path(__file__).parent / "data"


class TestGetParser:
    """Tests for the get_parser utility function"""

    def test_name_map_match(self):
        """Assert that name map functionality is performing as expected"""
        name_map = {"example_kv_1.tsv": tsv.TSVKeyValueParser}
        ext_map = {}
        parser = factory.get_parser(DATA_PATH / "example_kv_1.tsv", name_map=name_map, ext_map=ext_map)

        assert isinstance(parser, tsv.TSVKeyValueParser)
        assert parser.file_path == DATA_PATH / "example_kv_1.tsv"

    def test_ext_map_match(self):
        """Assert that extension map functionality is performing as expected"""
        name_map = {}
        ext_map = {".tsv": tsv.TSVKeyValueParser}
        parser = factory.get_parser(DATA_PATH / "example_kv_1.tsv", name_map=name_map, ext_map=ext_map)

        assert isinstance(parser, tsv.TSVKeyValueParser)
        assert parser.file_path == DATA_PATH / "example_kv_1.tsv"

    def test_name_map_priority(self):
        """Assert that the name map takes priority over the extension map as the extension map should be more general"""
        name_map = {"example_kv_1.tsv": tsv.TSVKeyValueParser}
        ext_map = {".tsv": tsv.TSVDataFrameParser}
        parser = factory.get_parser(DATA_PATH / "example_kv_1.tsv", name_map=name_map, ext_map=ext_map)

        assert isinstance(parser, tsv.TSVKeyValueParser)
        assert parser.file_path == DATA_PATH / "example_kv_1.tsv"

    def test_no_match(self):
        """Assert that None is returned when no valid parser is found"""
        name_map = {"example_kv_1.tsv": tsv.TSVKeyValueParser}
        ext_map = {".tsv": tsv.TSVDataFrameParser}
        parser = factory.get_parser(DATA_PATH / "example_kv_1.csv", name_map=name_map, ext_map=ext_map)

        assert parser is None

    def test_ext_map_csv(self):
        """Test that the general purpose CSV file matcher is correctly configured"""
        parser = factory.get_parser(DATA_PATH / "example_kv_1.csv", name_map={})

        assert isinstance(parser, csv.CSVDataFrameParser)
        assert parser.file_path == DATA_PATH / "example_kv_1.csv"

    def test_ext_map_json(self):
        """Test that the general purpose JSON file matcher is correctly configured"""
        parser = factory.get_parser(DATA_PATH / "example_1.json", name_map={})

        assert isinstance(parser, json_parse.JSONParser)
        assert parser.file_path == DATA_PATH / "example_1.json"

    def test_ext_map_tsv(self):
        """Test that the general purpose TSV file matcher is correctly configured"""
        parser = factory.get_parser(DATA_PATH / "example_kv_1.tsv", name_map={})

        assert isinstance(parser, tsv.TSVDataFrameParser)
        assert parser.file_path == DATA_PATH / "example_kv_1.tsv"
