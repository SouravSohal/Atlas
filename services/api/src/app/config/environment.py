from enum import StrEnum


class Environment(StrEnum):
    """Execution environment for the ATLAS system."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
