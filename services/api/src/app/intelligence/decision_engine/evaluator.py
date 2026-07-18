from typing import Any


class DecisionEvaluator:
    """Evaluates stadium recommendations against current operations states."""

    def filter_valid_recommendations(self, recommendations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensures decisions are only evaluated for pre-existing recommendations."""
        return [r for r in recommendations if r.get("id") or r.get("details")]
