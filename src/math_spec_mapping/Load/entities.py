from typing import Dict
from ..Classes import Entity
from .general import check_json_keys


def convert_entity(data: Dict, ms: Dict) -> Entity:
    """Convert the entity dictionary to an object

    Args:
        data (Dict): The entity data
        ms (Dict): MathSpec dictionary

    Returns:
        Entity: An entity object
    """

    if "metadata" not in data:
        data["metadata"] = {}
    # Check the keys are correct
    check_json_keys(data, "Entity")

    # Copy
    data = data.copy()

    # Assert that the state is in the math spec and assign it here
    if data["state"]:
        name = data["state"]
        pattern = data.get("pattern")

        # Check global states first
        if name in ms["State"]:
            data["state"] = ms["State"][name]
        # Then check pattern-specific states
        elif pattern:
            pattern_states_key = f"{pattern}_States"
            if pattern_states_key in ms and name in ms[pattern_states_key]:
                data["state"] = ms[pattern_states_key][name]
            else:
                raise KeyError(
                    f"{name} state not in states dictionary for the entity of {data['name']}"
                )
        else:
            raise KeyError(
                f"{name} state not in states dictionary for the entity of {data['name']}"
            )

    # Build the state object
    return Entity(data)


def load_entities(ms: Dict, json: Dict, pattern: str = None) -> None:
    """Function to load entities into the new dictionary

    Args:
        ms (Dict): MathSpec dictionary
        json (Dict): JSON version of MathSpec to load
        pattern (str): Optional pattern name for pattern-based specs
    """

    ms["Entities"] = {}

    for e in json["Entities"]:
        ms["Entities"][e["name"]] = convert_entity(e, ms)

    # Allow pattern-based entities
    if "Global" not in ms["Entities"]:
        if not json.get("pattern_metadata"):
            import warnings
            warnings.warn("No Global entity found. Using pattern-based entity organization.")
