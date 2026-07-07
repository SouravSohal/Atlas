from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base class for all value objects in the domain.

    Value objects are immutable and defined by their attributes rather than identity.
    """
