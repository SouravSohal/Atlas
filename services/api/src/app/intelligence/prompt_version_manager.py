class PromptVersionManager:
    """Manages raw prompt templates and their versions."""

    def __init__(self) -> None:
        self._templates: dict[str, dict[str, str]] = {
            "default": {
                "v1": "Analyze the following context and return JSON: {context}"
            }
        }

    def get_template(self, name: str, version: str = "latest") -> str:
        """Retrieves a prompt template by name and version."""
        if name not in self._templates:
            raise ValueError(f"Prompt template '{name}' not found.")

        versions = self._templates[name]
        if version == "latest":
            latest_version = sorted(versions.keys())[-1]
            return versions[latest_version]

        if version not in versions:
            raise ValueError(f"Version '{version}' for template '{name}' not found.")
        return versions[version]

    def register_template(self, name: str, version: str, template: str) -> None:
        """Registers a new template or version dynamically."""
        if name not in self._templates:
            self._templates[name] = {}
        self._templates[name][version] = template
