from typing import Any

import structlog
from atlas_core.domain.exceptions.domain_error import DomainException
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.presentation.responses import ApiResponse

logger = structlog.get_logger()

def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for the FastAPI application."""

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        logger.warning("Domain exception occurred", error_message=str(exc))
        response_data = ApiResponse[None](
            success=False,
            error=exc.message,
            request_id=request.headers.get("X-Request-ID"),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response_data.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Request validation failed", errors=exc.errors())
        response_data = ApiResponse[list[Any]](
            success=False,
            error="Validation failed",
            data=list(exc.errors()),
            request_id=request.headers.get("X-Request-ID"),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data.model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled server exception occurred", error=str(exc), exc_info=True)
        response_data = ApiResponse[None](
            success=False,
            error="An unexpected internal server error occurred.",
            request_id=request.headers.get("X-Request-ID"),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data.model_dump(),
        )
