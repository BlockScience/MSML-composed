from typing import Dict
from ..Classes import State, StateVariable
from .general import check_json_keys


def convert_state(ms, data: Dict) -> State:
    """_summary_

    Args:
        data (Dict): _description_

    Returns:
        State: _description_
    """
    if "metadata" not in data:
        data["metadata"] = {}

    # Check the keys are correct
    check_json_keys(data, "State")

    # Copy
    data = data.copy()

    # Convert the variables
    new_variables = []
    for var in data["variables"]:
        check_json_keys(var, "State Variable")
        assert var["type"] in ms["Types"], "Type {} referenced by {} not in ms".format(
            var["type"], var["name"]
        )
        var["type"] = ms["Types"][var["type"]]
        if "metadata" not in var:
            var["metadata"] = {}
        new_variables.append(StateVariable(var))
    data["variables"] = new_variables

    # Build the state object
    return State(data)


def load_states(ms: Dict, json: Dict, pattern: str = None) -> None:
    """Function to load states into the new dictionary

    Args:
        ms (Dict): MathSpec dictionary
        json (Dict): JSON version of MathSpec to load
        pattern (str): Optional pattern name for pattern-based specs
    """

    ms["State"] = {}

    for state in json["State"]:
        ms["State"][state["name"]] = convert_state(ms, state)

    # Allow pattern-based states or provide fallback
    if "Global State" not in ms["State"]:
        # Check if pattern metadata indicates pattern-based organization
        if not json.get("pattern_metadata"):
            # Only warn for non-pattern specs
            import warnings
            warnings.warn("No Global State found. Using pattern-based state organization.")
