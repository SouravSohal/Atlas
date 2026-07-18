from uuid import UUID

from app.application.scenario_simulator.models import SimulationRecord


class SimulationHistory:
    """Manages the history of simulated scenario executions in-memory."""

    def __init__(self) -> None:
        self._history: dict[UUID, SimulationRecord] = {}

    def add(self, record: SimulationRecord) -> None:
        """Adds a simulation record to the log history."""
        self._history[record.id] = record

    def list(self) -> list[SimulationRecord]:
        """Lists all simulation records sorted by timestamp descending."""
        return sorted(self._history.values(), key=lambda r: r.timestamp, reverse=True)

    def get(self, id: UUID) -> SimulationRecord | None:
        """Retrieves a simulation record by its ID."""
        return self._history.get(id)

    def clear(self) -> None:
        """Clears the history."""
        self._history.clear()
