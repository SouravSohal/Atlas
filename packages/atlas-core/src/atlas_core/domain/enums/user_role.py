from enum import StrEnum


class UserRole(StrEnum):
    """Represents the authorization and operational roles of users within the ATLAS ecosystem."""

    ADMIN = "admin"
    OPERATOR = "operator"
    VOLUNTEER = "volunteer"
    FAN = "fan"
    ATHLETE = "athlete"

    def is_staff(self) -> bool:
        """Determines if the role belongs to stadium staff/administrators."""
        return self in (UserRole.ADMIN, UserRole.OPERATOR)
