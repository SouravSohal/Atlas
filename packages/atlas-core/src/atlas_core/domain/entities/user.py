from dataclasses import dataclass

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.enums.user_role import UserRole
from atlas_core.domain.exceptions.validation_error import ValidationException


@dataclass(kw_only=True)
class User(BaseEntity):
    """Represents a registered user in the ATLAS system."""

    name: str
    role: UserRole
    email: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name.strip():
            raise ValidationException("User name cannot be empty.")
        if "@" not in self.email or not self.email.strip():
            raise ValidationException("User email must be a valid email address.")

    def update_role(self, new_role: UserRole) -> None:
        """Update the user's operational role."""
        self.role = new_role
