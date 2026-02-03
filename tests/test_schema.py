"""Tests for MSML schema and basic loading functionality."""

import json
from pathlib import Path

import pytest


SCHEMA_PATH = Path(__file__).parent.parent / "src" / "math_spec_mapping" / "schema.schema.json"


@pytest.fixture
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture
def msml_spec_def(schema):
    """The MSMLSpec definition within the schema."""
    return schema["definitions"]["MSMLSpec"]


class TestSchemaValidity:
    """Ensure the JSON schema itself is valid."""

    def test_schema_file_exists(self):
        assert SCHEMA_PATH.exists()

    def test_schema_is_valid_json(self):
        with open(SCHEMA_PATH) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_schema_has_definitions(self, schema):
        assert "definitions" in schema
        assert "MSMLSpec" in schema["definitions"]

    def test_msml_spec_has_core_components(self, msml_spec_def):
        props = msml_spec_def["properties"]
        for component in [
            "Policies",
            "Spaces",
            "State",
            "Mechanisms",
            "Entities",
            "Types",
            "Parameters",
            "Boundary Actions",
            "Control Actions",
            "Wiring",
            "Stateful Metrics",
            "Metrics",
        ]:
            assert component in props, f"{component} missing from MSMLSpec"


class TestPatternFields:
    """Ensure pattern-specific schema extensions are present."""

    def test_pattern_metadata_in_spec(self, msml_spec_def):
        props = msml_spec_def["properties"]
        assert "pattern_metadata" in props, "pattern_metadata field missing from MSMLSpec"

    def test_pattern_metadata_structure(self, msml_spec_def):
        pm = msml_spec_def["properties"]["pattern_metadata"]
        pm_props = pm.get("properties", {})
        assert "patterns" in pm_props, "patterns array missing from pattern_metadata"
        assert "primary_pattern" in pm_props, "primary_pattern missing from pattern_metadata"

    def test_policy_has_pattern_field(self, schema):
        policy_def = schema["definitions"]["Policy"]
        assert "pattern" in policy_def["properties"]

    def test_mechanism_has_pattern_field(self, schema):
        mechanism_def = schema["definitions"]["Mechanism"]
        assert "pattern" in mechanism_def["properties"]

    def test_space_has_pattern_field(self, schema):
        space_def = schema["definitions"]["Space"]
        assert "pattern" in space_def["properties"]

    def test_wiring_has_notes_field(self, schema):
        wiring_def = schema["definitions"]["Wiring"]
        assert "notes" in wiring_def["properties"]


class TestImports:
    """Ensure the package imports correctly."""

    def test_import_math_spec_mapping(self):
        import math_spec_mapping

        assert hasattr(math_spec_mapping, "load_from_json")

    def test_import_load_from_json(self):
        from math_spec_mapping import load_from_json

        assert callable(load_from_json)

    def test_import_write_functions(self):
        from math_spec_mapping import write_all_markdown_reports, write_spec_tree

        assert callable(write_all_markdown_reports)
        assert callable(write_spec_tree)
