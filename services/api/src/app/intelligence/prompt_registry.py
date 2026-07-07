from app.intelligence.exceptions import PromptNotFoundException
from app.intelligence.prompt_version import PromptVersion


class PromptRegistry:
    """Registers, stores, and looks up prompt templates and versions."""

    def __init__(self) -> None:
        self._registry: dict[str, dict[str, PromptVersion]] = {}

    def register(self, name: str, version: str, template: str, description: str = "") -> None:
        """Registers a new prompt version in the registry."""
        if name not in self._registry:
            self._registry[name] = {}
        self._registry[name][version] = PromptVersion(
            version=version,
            template=template,
            description=description,
        )

    def get(self, name: str, version: str = "latest") -> PromptVersion:
        """Retrieves a specific or latest version of a prompt template."""
        if name not in self._registry or not self._registry[name]:
            raise PromptNotFoundException(f"Prompt template '{name}' is not registered.")

        versions = self._registry[name]
        if version == "latest":
            latest_key = sorted(versions.keys())[-1]
            return versions[latest_key]

        if version not in versions:
            raise PromptNotFoundException(f"Version '{version}' of prompt template '{name}' not found.")

        return versions[version]
