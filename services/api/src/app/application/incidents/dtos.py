from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateIncidentRequest(BaseModel):
    """Request payload for reporting/creating a new incident."""

    incident_type: str = Field(..., description="Classification of the incident (e.g. security, medical).")
    severity: str = Field(..., description="Severity level of the incident (e.g. low, high, critical).")
    description: str = Field(..., description="Detailed description of the incident.")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinates of the incident.")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinates of the incident.")
    reporter_id: UUID = Field(..., description="Unique ID of the user reporting the incident.")
    zone_id: UUID = Field(..., description="Unique ID of the stadium zone where the incident occurred.")


class UpdateIncidentRequest(BaseModel):
    """Request payload for patching/updating an existing incident."""

    resolved: bool | None = Field(None, description="Resolution status of the incident.")
    severity: str | None = Field(None, description="Severity level of the incident.")
    description: str | None = Field(None, description="Detailed description of the incident.")


class IncidentResponse(BaseModel):
    """Standardized incident details response payload."""

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
