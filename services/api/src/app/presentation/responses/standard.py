from pydantic import BaseModel, Field


class ApiResponse[T](BaseModel):
    """Standard uniform API response structure for all endpoints."""

    success: bool = Field(..., description="Whether the request succeeded.")
    data: T | None = Field(default=None, description="The payload of the response.")
    error: str | None = Field(default=None, description="Error message if success is false.")
    request_id: str | None = Field(default=None, description="The unique ID of the request.")
