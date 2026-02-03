import ast
import glob
import os


def index_to_line_and_column(lines, index):
    cumulative_length = 0
    for line_number, line in enumerate(lines):
        line_length = len(line) + 1  # +1 for the newline character
        if cumulative_length + line_length > index:
            column = index - cumulative_length
            return line_number, column
        cumulative_length += line_length

    raise ValueError("Index out of range")


def _collect_search_dirs(path, folder):
    """Collect all directories to search for a given component folder.

    Returns directories in priority order:
    1. {path}/{folder}/ (legacy flat structure)
    2. {path}/shared/{folder}/ (shared components)
    3. {path}/patterns/*/{folder}/ (auto-discovered patterns, sorted)

    Only includes directories that exist and contain __init__.py.
    """
    dirs = []

    # 1. Legacy flat path
    legacy = os.path.join(path, folder)
    if os.path.isdir(legacy) and os.path.isfile(
        os.path.join(legacy, "__init__.py")
    ):
        dirs.append(legacy)

    # 2. Shared path
    shared = os.path.join(path, "shared", folder)
    if os.path.isdir(shared) and os.path.isfile(
        os.path.join(shared, "__init__.py")
    ):
        dirs.append(shared)

    # 3. Pattern paths (auto-discovered, sorted for determinism)
    patterns_glob = os.path.join(path, "patterns", "*", folder)
    for pattern_dir in sorted(glob.glob(patterns_glob)):
        if (
            os.path.isdir(pattern_dir)
            and "__pycache__" not in pattern_dir
            and os.path.isfile(os.path.join(pattern_dir, "__init__.py"))
        ):
            dirs.append(pattern_dir)

    return dirs


def _scan_dir_for_keys(dir_path, keys, found):
    """Scan a directory's __init__.py (and its submodules) for component names.

    Uses two strategies:
    - Strategy A: Parse __init__.py AST, follow ImportFrom to submodule .py files,
      search those files for component names (existing behavior).
    - Strategy B: Search __init__.py itself for inline component definitions.

    Args:
        dir_path: Directory containing __init__.py
        keys: List of component names to search for
        found: Dict mapping component name -> "abspath#Lnnn" (mutated in place)
    """
    init_path = os.path.join(dir_path, "__init__.py")
    if not os.path.isfile(init_path):
        return

    remaining = [k for k in keys if k not in found]
    if not remaining:
        return

    try:
        with open(init_path, "r") as f:
            init_contents = f.read()
    except (IOError, OSError):
        return

    try:
        tree = ast.parse(init_contents, filename=init_path)
    except SyntaxError:
        return

    # Strategy A: Follow ImportFrom nodes to submodule files
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            submodule_path = os.path.join(dir_path, node.module + ".py")
            if not os.path.isfile(submodule_path):
                continue

            try:
                with open(submodule_path, "r") as f2:
                    contents = f2.read()
            except (IOError, OSError):
                continue

            split = contents.split("\n")
            for key in remaining:
                if key not in found and key in contents:
                    line_number = (
                        index_to_line_and_column(split, contents.index(key))[0]
                        + 1
                    )
                    found[key] = os.path.abspath(submodule_path) + "#L{}".format(
                        line_number
                    )

    # Strategy B: Search __init__.py itself for inline definitions
    remaining = [k for k in keys if k not in found]
    if not remaining:
        return

    init_split = init_contents.split("\n")
    for key in remaining:
        if key in init_contents:
            line_number = (
                index_to_line_and_column(init_split, init_contents.index(key))[0]
                + 1
            )
            found[key] = os.path.abspath(init_path) + "#L{}".format(line_number)


def load_spec_tree(path, ms):
    tree = {}
    for folder in [
        "StatefulMetrics",
        "Metrics",
        "Mechanisms",
        "BoundaryActions",
        "Types",
        "ControlActions",
        "Displays",
        "Spaces",
        "State",
        "Policies",
        "Wiring",
        "Parameters",
        "Entities",
    ]:
        if folder == "StatefulMetrics":
            keys = ms.get_all_stateful_metric_names()
        elif folder == "Metrics":
            keys = ms.metrics.keys()
        elif folder == "Mechanisms":
            keys = ms.mechanisms.keys()
        elif folder == "BoundaryActions":
            keys = ms.boundary_actions.keys()
        elif folder == "Types":
            keys = ms.types.keys()
        elif folder == "ControlActions":
            keys = ms.control_actions.keys()
        elif folder == "Displays":
            keys = [x["name"] for x in ms.displays["Wiring"]]
        elif folder == "Spaces":
            keys = ms.spaces.keys()
        elif folder == "State":
            keys = ms.state.keys()
        elif folder == "Policies":
            keys = ms.policies.keys()
        elif folder == "Wiring":
            keys = ms.wiring.keys()
        elif folder == "Parameters":
            keys = ms.parameters.all_parameters
        elif folder == "Entities":
            keys = ms.entities.keys()
        else:
            assert False
        keys = list(keys)
        found = {}

        search_dirs = _collect_search_dirs(path, folder)
        for search_dir in search_dirs:
            _scan_dir_for_keys(search_dir, keys, found)
            # Early exit if all keys found
            if len(found) >= len(keys):
                break

        tree[folder] = found

    return tree
