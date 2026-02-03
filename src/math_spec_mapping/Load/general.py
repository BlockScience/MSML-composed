from typing import Dict
from jsonschema import validate
from ..schema import schema


def check_json_keys(json: Dict, check_set_key: str) -> None:
    pass
    """Function to check the correct keys are in the json dictionary

    Args:
        json (Dict): MathSpec json formatted dictionary
        check_set_key (str): The key for what checking set to use
    """

    """# Get a temporary list of keys
    keys = list(json.keys())

    # Pick the correct checking set
    check_sets = {
        "Math Spec": [
            "Action Transmission Channels",
            "Boundary Actions",
            "Entities",
            "Mechanisms",
            "Parameters",
            "Policies",
            "Spaces",
            "State",
            "State Update Transmission Channels",
            "Stateful Metrics",
            "Control Actions",
            "Wiring",
            "Blocks",
            "Types",
            "Metrics",
        ],
        "JSON": [
            "Boundary Actions",
            "Entities",
            "Mechanisms",
            "Parameters",
            "Policies",
            "Spaces",
            "State",
            "Stateful Metrics",
            "Control Actions",
            "Wiring",
            "Types",
            "Metrics",
            "Displays",
        ],
        "State": ["name", "label", "notes", "variables", "metadata"],
        "State Variable": ["type", "name", "description", "symbol", "domain"],
        "Entity": ["name", "notes", "state", "metadata"],
        "Boundary Action": [
            "name",
            "label",
            "description",
            "constraints",
            "boundary_action_options",
            "called_by",
            "codomain",
            "parameters_used",
            "metadata",
        ],
        "Action Transmission Channel": ["origin", "target", "space", "optional"],
        "Mechanism": [
            "name",
            "label",
            "description",
            "constraints",
            "logic",
            "domain",
            "parameters_used",
            "metadata",
            "updates",
        ],
        "State Update Transmission Channel": [
            "origin",
            "entity",
            "variable",
            "optional",
        ],
        "Policy": [
            "name",
            "label",
            "description",
            "constraints",
            "policy_options",
            "domain",
            "codomain",
            "parameters_used",
            "metadata",
        ],
        "Policy Option": ["name", "description", "logic"],
        "Stateful Metric Set": ["name", "label", "notes", "metrics", "metadata"],
        "Stateful Metric": [
            "type",
            "name",
            "label",
            "description",
            "variables_used",
            "parameters_used",
            "symbol",
            "domain",
            "metadata",
        ],
        "Control Action": [
            "name",
            "label",
            "description",
            "constraints",
            "control_action_options",
            "codomain",
            "parameters_used",
            "metadata",
        ],
        "Control Action Option": ["name", "description", "logic"],
        "Boundary Action Option": ["name", "description", "logic"],
        "Parameter Set": ["name", "notes", "parameters", "metadata"],
        "Parameter": [
            "variable_type",
            "name",
            "description",
            "symbol",
            "domain",
            "parameter_class",
            "metadata",
        ],
        "Space": ["name", "schema", "metadata"],
        "Block": [
            "name",
            "components",
            "description",
            "constraints",
            "mermaid_show_name",
            "loop",
            "optional_indices",
            "metadata",
        ],
        "Type": ["name", "notes", "metadata", "type"],
    }

    check_set = check_sets[check_set_key]

    # Check each key is in the json
    for k in check_set:
        # Can skip if it is label
        if k == "label":
            if k in keys:
                keys.remove(k)
        else:
            assert k in keys, "{} not in json keys".format(k)
            keys.remove(k)

    # Make sure there are no extra keys in the json
    assert len(keys) == 0, "There are extra keys in json: {}".format(", ".join(keys))"""


def validate_json_schema(json):
    validate(json, schema)


def resolve_space(space_name: str, ms: Dict, pattern: str = None) -> bool:
    """
    Resolve space name with pattern awareness.

    Lookup hierarchy:
    1. Global spaces (ms["Spaces"])
    2. Pattern-specific spaces (ms["<pattern>_Spaces"])
    3. Shared spaces

    Args:
        space_name: Name of the space to resolve
        ms: MathSpec dictionary
        pattern: Optional pattern name for pattern-specific lookup

    Returns:
        True if space exists, False otherwise
    """
    if space_name in ms["Spaces"]:
        return True

    if pattern:
        pattern_spaces_key = f"{pattern}_Spaces"
        if pattern_spaces_key in ms and space_name in ms[pattern_spaces_key]:
            return True

    return False


def check_domain_codomain_spaces(json: Dict, ms, pattern: str = None) -> None:
    if "domain" in json:
        for key in json["domain"]:
            assert resolve_space(key, ms, pattern), "{} not in spaces".format(key)
    if "codomain" in json:
        for key in json["codomain"]:
            assert resolve_space(key, ms, pattern), "{} not in spaces".format(key)
