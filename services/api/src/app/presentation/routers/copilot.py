from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.application.copilot.models import CopilotChatRequest, CopilotChatResponse
from app.application.copilot.service import CopilotService
from app.dependencies.auth import get_current_user
from app.dependencies.container import ApplicationContainer
from app.infrastructure.security.rate_limiter import RateLimiterDependency
from app.presentation.responses import ApiResponse

router = APIRouter(
    prefix="/copilot",
    tags=["Copilot"],
    dependencies=[Depends(get_current_user), Depends(RateLimiterDependency("copilot"))]
)

@router.post("/chat", response_model=ApiResponse[CopilotChatResponse])
@inject
async def copilot_chat(
    request: CopilotChatRequest,
    copilot_service: CopilotService = Depends(Provide[ApplicationContainer.copilot_service]),
) -> ApiResponse[CopilotChatResponse]:
    """Exposes chat endpoint for ATLAS Copilot cognitive assistant."""
    response = await copilot_service.chat(request)
    return ApiResponse(success=True, data=response)
