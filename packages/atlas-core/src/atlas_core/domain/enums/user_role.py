from enum import StrEnum


class UserRole(StrEnum):
    """Represents the authorization and operational roles of users within the ATLAS ecosystem."""

    ADMIN = "admin"
    OPERATOR = "operator"
    VOLUNTEER = "volunteer"
    FAN = "fan"
    ATHLETE = "athlete"

    # New enterprise roles
    ADMINISTRATOR = "administrator"
    OPERATIONS_COMMANDER = "operations_commander"
    SECURITY_OFFICER = "security_officer"
    MEDICAL_COORDINATOR = "medical_coordinator"
    VOLUNTEER_COORDINATOR = "volunteer_coordinator"
    EXECUTIVE_OBSERVER = "executive_observer"

    def is_staff(self) -> bool:
        """Determines if the role belongs to stadium staff/administrators."""
        return self in (
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.ADMINISTRATOR,
            UserRole.OPERATIONS_COMMANDER,
            UserRole.SECURITY_OFFICER,
            UserRole.MEDICAL_COORDINATOR,
            UserRole.VOLUNTEER_COORDINATOR,
            UserRole.EXECUTIVE_OBSERVER,
        )
