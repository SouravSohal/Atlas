# ATLAS Core Package (`atlas-core`)

An enterprise-grade, domain-driven core package for the **ATLAS** system.

## Project Architecture

This package represents the core domain and shared utilities of the system, adhering strictly to **Domain-Driven Design (DDD)** and **Clean Architecture** principles.

### Package Layout (src-layout)

```
packages/atlas-core/
├── pyproject.toml              # Build, dependency, and tool configuration
├── README.md                   # Package documentation
├── src/
│   └── atlas_core/             # Exported import package
│       ├── __init__.py
│       ├── domain/             # Core DDD domain model layers
│       │   ├── __init__.py
│       │   ├── entities/       # Mutable domain objects with identities
│       │   ├── enums/          # Domain-specific enums
│       │   ├── events/         # Domain events emitted upon state changes
│       │   ├── exceptions/     # Domain-specific business rule violations
│       │   ├── repositories/   # Interfaces/contracts for persistence layers
│       │   ├── services/       # Domain services containing coordinate logic
│       │   └── value_objects/  # Immutable domain values without identity
│       └── shared/             # Shared kernel utilities & primitives
│           ├── __init__.py
│           ├── constants.py
│           └── types.py
└── tests/                      # Pytest suite mapping to package modules
```

## Development and Tooling

### Installation

This package is configured with **Hatchling** as the build backend, using the standardized Python `src-layout`.

To install the package locally in editable mode:

```bash
pip install -e packages/atlas-core
```

### Testing

Run the tests inside the package using `pytest`:

```bash
pytest packages/atlas-core/tests
```

### Static Analysis

This package enforces strict typing and linting standards:

- **Type Checking**: Strict `mypy` type hints are required for all public APIs.
- **Linting**: Standardized `ruff` rules apply to preserve code health and style uniformity.
