from typing import Any

from app.infrastructure.firestore.exceptions import ConcurrencyException


class OptimisticLockManager:
    """Manages optimistic locking attributes and validations for Firestore documents."""

    @staticmethod
    def increment_version(data: dict[str, Any]) -> dict[str, Any]:
        """Increments the version attribute of the document data."""
        updated = data.copy()
        current_version = updated.get("version", 0)
        updated["version"] = current_version + 1
        return updated

    @staticmethod
    def check_version(current_data: dict[str, Any] | None, expected_version: int | None) -> None:
        """Verifies if the version of the current document matches the expected version.

        Raises ConcurrencyException if a conflict is detected.
        """
        if expected_version is None:
            return

        if current_data is None:
            raise ConcurrencyException(
                "Cannot perform write operation: Document does not exist."
            )

        actual_version = current_data.get("version", 0)
        if actual_version != expected_version:
            raise ConcurrencyException(
                f"Optimistic lock conflict: Expected version {expected_version}, but found {actual_version}."
            )
