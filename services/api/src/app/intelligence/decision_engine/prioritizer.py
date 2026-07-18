
from app.intelligence.decision_engine.models import DecisionItem


class DecisionPrioritizer:
    """Prioritizes decisions according to priority weightings and computed risk scores."""

    def prioritize(self, decisions: list[DecisionItem]) -> list[DecisionItem]:
        """Sorts decision items by severity and priority weights."""
        priority_weights = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        return sorted(
            decisions,
            key=lambda d: (priority_weights.get(d.priority.lower(), 0), d.confidence),
            reverse=True
        )
