"""Test harness and utilities for software testing"""

import json
from pathlib import Path

HYALUS_METADATA = Path(__file__).parent / "metadata.json"

with open(HYALUS_METADATA, 'r', encoding="utf-8") as json_fh:
    __version__ = json.load(json_fh)["version"]
