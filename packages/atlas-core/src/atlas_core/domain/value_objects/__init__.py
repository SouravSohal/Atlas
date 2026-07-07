"""Domain value objects."""

from atlas_core.domain.value_objects.base import ValueObject
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate

__all__ = [
    "ConfidenceScore",
    "Coordinates",
    "CrowdDensity",
    "QueueEstimate",
    "ValueObject",
]
