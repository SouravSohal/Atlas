from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DashboardOverviewResponse(BaseModel):
    """General overview metrics of the stadium operations."""

    stadium_health: float = Field(..., description="Overall stadium health score from 0.0 to 1.0.")
    active_incidents_count: int = Field(..., description="Total count of active unresolved incidents.")
    average_crowd_density: float = Field(..., description="Average crowd density across all stadium zones.")
    pending_recommendations_count: int = Field(..., description="Total count of pending recommendations.")
    allocated_volunteers_count: int = Field(..., description="Total count of active volunteers assigned to tasks.")
    timestamp: datetime = Field(..., description="Time of the overview compilation.")


class IncidentDashboardItem(BaseModel):
    """Represent an incident in the dashboard query."""

    id: UUID
    incident_type: str
    severity: str
    description: str
    latitude: float
    longitude: float
    reporter_id: UUID
    resolved: bool
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class IncidentDashboardListResponse(BaseModel):
    """Paginated list response of incidents."""

    total_count: int
    page: int
    limit: int
    items: list[IncidentDashboardItem]


class OperationalStateDashboardItem(BaseModel):
    """Represent zone operational state details in the dashboard."""

    zone_id: UUID
    density: float
    queue_waiting_minutes: int
    last_updated: datetime


class RecommendationDashboardItem(BaseModel):
    """Represent a recommendation in the dashboard query."""

    id: UUID
    action_type: str
    priority: str
    confidence: float
    details: str
    status: str
    approved_by_id: UUID | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RecommendationDashboardListResponse(BaseModel):
    """Paginated list response of recommendations."""

    total_count: int
    page: int
    limit: int
    items: list[RecommendationDashboardItem]


class DashboardMetricsResponse(BaseModel):
    """Detailed telemetry and operational metrics for graphical charts."""

    average_queue_wait_minutes: float = Field(..., description="Average queue wait time across all zones.")
    congestion_rate: float = Field(..., description="Ratio of zones with crowd density > 0.75.")
    incident_resolution_rate: float = Field(..., description="Ratio of resolved incidents to total incidents.")
    incidents_by_severity: dict[str, int] = Field(..., description="Count of incidents grouped by severity level.")
    incidents_by_type: dict[str, int] = Field(..., description="Count of incidents grouped by type.")
    recommendations_by_status: dict[str, int] = Field(..., description="Count of recommendations grouped by status.")
