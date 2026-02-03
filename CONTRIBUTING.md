# Contributing to MSML (Pattern-Aware Fork)

This is a fork of [BlockScience/MSML-composed](https://github.com/BlockScience/MSML-composed) with native pattern-based organization support. This guide covers setting up a development environment and contributing changes.

## Development Setup

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install with uv

```bash
# Clone with submodules (if part of arkhai_msml)
git clone --recurse-submodules <repo-url>
cd msml-fork

# Create virtual environment and install
uv venv
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Install with pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### Verify Installation

```bash
python -c "import math_spec_mapping; print('MSML fork active')"
```

## Development Workflow

### Common Commands

```bash
make help          # Show all available commands
make format        # Format code (black + ruff isort)
make lint          # Lint code (ruff)
make type-check    # Type check (mypy)
make test          # Run tests
make test-cov      # Run tests with coverage
make clean         # Remove build artifacts
```

### Code Quality

All code must pass formatting and linting before commit. Pre-commit hooks enforce this automatically.

**Formatting**: [Black](https://black.readthedocs.io/) with 100 character line length.

**Linting**: [Ruff](https://docs.astral.sh/ruff/) checking for pycodestyle, pyflakes, isort, bugbear, and pyupgrade rules.

**Type checking**: [mypy](https://mypy-lang.org/) with `ignore_missing_imports` enabled (upstream MSML has incomplete type annotations).

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/test_pattern_loading.py -v

# With coverage report
make test-cov
```

### Skip Pre-commit Hooks

For documentation-only changes when hooks fail on unrelated files:

```bash
git commit --no-verify -m "docs: update README"
```

## Project Structure

```
src/math_spec_mapping/
├── Classes/          # Core data classes (Block, Policy, Mechanism, etc.)
├── Convenience/      # Helper utilities (cadCAD, documentation, github)
├── Load/             # JSON spec loading (pattern-aware)
├── Reports/          # Report generation (markdown, HTML, wiring diagrams)
├── __init__.py       # Public API exports
├── schema.py         # JSON Schema wrapper
└── schema.schema.json # Component validation schema
```

## Fork-Specific Features

This fork adds pattern-based organization support to MSML. Key modifications:

### Schema Changes (`schema.schema.json`)

- `pattern` field on all component types (Policy, Mechanism, Space, State, Wiring, Type)
- `pattern_metadata` in MSMLSpec (`patterns` array, `primary_pattern` field)
- `notes` field on Wiring definitions
- `Composite` wiring type in TypeEnum
- Global State/Entity requirements now optional for pattern-based specs

### Loading Infrastructure (`Load/`)

- Pattern-aware space/state resolution with fallback hierarchy in `general.py`
- Pattern context propagated through all loaders (`policy.py`, `mechanism.py`, `entities.py`, etc.)
- Pattern field stored in Block instances
- Multi-directory spec tree resolution in `spec_tree.py`

### Pattern Resolution

```python
# Hierarchical space lookup order:
# 1. Global spaces (ms["Spaces"])
# 2. Pattern-specific spaces (ms["<pattern>_Spaces"])
# 3. Enables cross-pattern component references
```

## Making Changes

### Modifying the Schema

1. Edit `src/math_spec_mapping/schema.schema.json`
2. Update relevant loaders in `Load/` to handle new fields
3. Add tests for the new schema fields
4. Test with pattern loading from the parent project:
   ```bash
   cd /path/to/arkhai_msml
   python -c "from src import load_pattern; load_pattern('open_games')"
   ```

### Modifying Loaders

1. Edit the relevant file in `Load/`
2. Maintain backward compatibility (new fields should be optional)
3. Test with both pattern-based and legacy monolithic specs
4. Run the full test suite

### Testing Fork Changes

Always test modifications with actual pattern loading:

```bash
# Test pattern metadata acceptance
python -c "
from src import load_pattern
from math_spec_mapping import load_from_json
spec = load_pattern('open_games', include_shared=True)
print(f'Loaded {len(spec[\"Types\"])} types')
"

# Test cross-pattern references
python -c "
from src import load_all_patterns
spec = load_all_patterns()
print(f'Combined: {len(spec[\"Types\"])} types, {len(spec[\"Policies\"])} policies')
"
```

## Syncing with Upstream

```bash
git remote add upstream https://github.com/BlockScience/MSML-composed.git
git fetch upstream
git merge upstream/main
# Resolve conflicts, focusing on preserving pattern-aware changes
# Test thoroughly after merge
make test
```

## Conventions

- Follow PEP 8 (enforced by Black and Ruff)
- Use type hints for public function signatures
- Add docstrings to new public functions (Google style)
- Keep backward compatibility with existing MSML specs
- Pattern-related parameters should always be optional with `None` default
