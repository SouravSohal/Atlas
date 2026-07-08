from typing import List, Dict, Any

class DecisionEvaluator:
    """Evaluates stadium recommendations against current operations states."""

    def filter_valid_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensures decisions are only evaluated for pre-existing recommendations."""
        return [r for r in recommendations if r.get("id") or r.get("details")]
