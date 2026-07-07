from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class PromptVersion:
    """Represents a specific version of a prompt template with its metadata."""

    version: str
    template: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    description: str = ""
