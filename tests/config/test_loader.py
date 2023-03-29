"""Tests for the hyalus.config.loader module"""

__author__ = "David McConnell"
__credits__ = ["David McConnell"]
__maintainer__ = "David McConnell"

from pathlib import Path

import pytest

from hyalus.config import common, loader

DATA_PATH = Path(__file__).parent / "data"


class TestConfigLoader:
    """Tests for the ConfigLoader class"""

    def test_load_module_pass(self):
        """Test valid python module parsing"""
        config_loader = loader.ConfigLoader(DATA_PATH / "pass.py")
        config_loader.run()

    def test_load_module_invalid_path(self):
        """Test handling of module path that does not exist"""
        with pytest.raises(common.InvalidHyalusConfig) as exc:
            config_loader = loader.ConfigLoader(DATA_PATH / "not_a_file.py")
            config_loader.run()

        assert str(exc.value) == common.ConfigStatus.NOT_FOUND.value

    def test_load_module_invalid_config(self):
        """Test handling of module that is not valid python"""
        with pytest.raises(common.InvalidHyalusConfig) as exc:
            config_loader = loader.ConfigLoader(DATA_PATH / "invalid_syntax.py")
            config_loader.run()

        assert str(exc.value) == common.ConfigStatus.COULD_NOT_BE_LOADED.value

    def test_load_module_missing_fields(self):
        """Test handling of module that does not have all of the required fields"""
        with pytest.raises(common.InvalidHyalusConfig) as exc:
            config_loader = loader.ConfigLoader(DATA_PATH / "missing_fields.py")
            config_loader.run()

        expected = (
            common.ConfigStatus.MISSING_FIELDS.value
            + f"\n\nMissing: {', '.join(sorted([loader.DESCRIPTION.name, loader.INPUT_DATA.name]))}"
        )

        assert str(exc.value) == expected

    def test_load_module_invalid_types(self):
        """Test handling of module that has required fields but some are incorrectly typed"""
        with pytest.raises(common.InvalidHyalusConfig) as exc:
            config_loader = loader.ConfigLoader(DATA_PATH / "invalid_types.py")
            config_loader.run()

        expected = f"{common.ConfigStatus.INVALID_FIELDS.value}\n"

        for field in loader.REQUIRED_FIELDS:
            expected += f"\ntype({field.name}) != {field.type}"

        assert str(exc.value) == expected

    def test_load_module_missing_tags(self):
        """Test handling of module that is missing required tags"""
        with pytest.raises(common.InvalidHyalusConfig) as exc:
            config_loader = loader.ConfigLoader(DATA_PATH / "missing_tags.py")
            config_loader.run()

        assert str(exc.value) == f"{common.ConfigStatus.INVALID_FIELDS.value}\n\nMissing tags with type: Runtime"
