from typing import Dict
from ..Classes import Mechanism
from .general import check_json_keys, check_domain_codomain_spaces


def convert_mechanism(data: Dict, ms: Dict, pattern: str = None) -> Mechanism:
    """Function to convert dictionary to mechanism object

    Args:
        data (Dict): The data to convert
        ms (Dict): MathSpec dictionary
        pattern (str): Optional pattern name for pattern-aware resolution

    Returns:
        Mechanism: Mechanism object
    """

    if "metadata" not in data:
        data["metadata"] = {}

    data["domain"] = tuple(data["domain"])

    # Check the keys are correct
    check_json_keys(data, "Mechanism")
    assert type(data["domain"]) == tuple, "{} domain is not a tuple".format(
        data["name"]
    )
    if len(data["domain"]) == 0:
        data["domain"] = ("Empty Space",)

    check_domain_codomain_spaces(data, ms, pattern=pattern)

    # Copy
    data = data.copy()

    new_channels = []
    updates = data.pop("updates")
    for x in updates:
        new_channels.append(
            {
                "origin": data["name"],
                "entity": x[0],
                "variable": x[1],
                "optional": x[2],
            }
        )

    data["domain"] = tuple(ms["Spaces"][x] for x in data["domain"])
    data["implementations"] = {}

    if "python" in ms["Implementations"]:
        if "mechanisms" in ms["Implementations"]["python"]:
            if data["name"] in ms["Implementations"]["python"]["mechanisms"]:
                data["implementations"]["python"] = ms["Implementations"]["python"][
                    "mechanisms"
                ][data["name"]]

    # Build the action transmission channel object
    return Mechanism(data), new_channels


def load_mechanisms(ms: Dict, json: Dict, pattern: str = None) -> None:
    """Function to load mechanisms into the new dictionary

    Args:
        ms (Dict): MathSpec dictionary
        json (Dict): JSON version of MathSpec to load
        pattern (str): Optional default pattern for components without explicit pattern
    """

    ms["Mechanisms"] = {}
    state_update_transmission_channels = []
    for m in json["Mechanisms"]:
        component_pattern = m.get("pattern", pattern)
        ms["Mechanisms"][m["name"]], new_channels = convert_mechanism(m, ms, pattern=component_pattern)
        state_update_transmission_channels.extend(new_channels)

        key = m["name"]
        for space in ms["Mechanisms"][key].domain:
            space.domain_blocks.append(ms["Mechanisms"][key])

        for space in ms["Mechanisms"][key].codomain:
            space.codomain_blocks.append(ms["Mechanisms"][key])
    return state_update_transmission_channels
