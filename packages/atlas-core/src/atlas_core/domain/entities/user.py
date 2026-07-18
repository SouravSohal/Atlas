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

    def can_access_security_zone(self, zone_category: str) -> bool:
        """Determines if the user's role grants access to a specific FIFA stadium security zone."""
        category_lower = zone_category.lower().strip()
        # Public access
        if category_lower in ("general_stands", "fan_zone", "concourse", "restroom", "parking"):
            return True
        # Staff and security access
        if self.role.is_staff():
            return True
        # Athlete access
        if self.role == UserRole.ATHLETE:
            return category_lower in ("pitch", "locker_room", "athlete_tunnel", "medical")
        # Volunteer access
        if self.role == UserRole.VOLUNTEER:
            return category_lower not in ("pitch", "locker_room", "vip_lounge")
        return False
