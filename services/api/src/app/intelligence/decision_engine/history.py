from typing import List
from app.intelligence.decision_engine.models import DecisionEngineResult

class DecisionHistory:
    """Maintains historical record of decisions evaluated by the engine in memory."""

    def __init__(self) -> None:
        self._history: List[DecisionEngineResult] = []

    def record(self, result: DecisionEngineResult) -> None:
        """Appends evaluated decisions container into history list."""
        self._history.append(result)

    def get_all(self) -> List[DecisionEngineResult]:
        """Returns all recorded decision results."""
        return self._history

    def clear(self) -> None:
        """Clears memory history log."""
        self._history.clear()
