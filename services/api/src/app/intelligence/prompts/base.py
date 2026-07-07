from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class PromptVersion:
    """Represents a specific version of a prompt template."""

    version: str
    template: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    description: str = ""


@dataclass(frozen=True)
class PromptMetadata:
    """Metadata detailing the prompt purpose, expected outputs, and constraints."""

    name: str
    description: str
    author: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: list[str] = field(default_factory=list)


class BasePrompt:
    """Base class representing a structured prompt component."""

    def __init__(self, metadata: PromptMetadata, versions: list[PromptVersion]) -> None:
        self.metadata = metadata
        self._versions = {v.version: v for v in versions}

    def get_version(self, version: str = "latest") -> PromptVersion:
        """Retrieves a specific version or the latest version from the prompt versions list."""
        if not self._versions:
            raise ValueError(f"No versions registered for prompt '{self.metadata.name}'.")
        if version == "latest":
            latest_key = sorted(self._versions.keys())[-1]
            return self._versions[latest_key]
        if version not in self._versions:
            raise ValueError(f"Version '{version}' for prompt '{self.metadata.name}' not found.")
        return self._versions[version]
