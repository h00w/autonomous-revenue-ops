import logging
import time
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Header, Request, Response

from .config import get_settings
from .logging_config import configure_logging
from .models import HealthResponse, LeadEvaluationRequest, WorkflowResponse
from .orchestration.api import router as workflow_router
from .service import RevenueOpsService

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)
service = RevenueOpsService(settings=settings)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.service_version,
        description="Production API boundary for governed revenue-operations workflows.",
    )

    @app.middleware("http")
    async def correlation_and_access_log(request: Request, call_next):
        started = time.perf_counter()
        correlation_id = request.headers.get("X-Correlation-ID") or f"corr_{uuid4().hex}"
        request.state.correlation_id = correlation_id
        response: Response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        logger.info(
            "http request completed",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response

    @app.get("/health/live", response_model=HealthResponse, tags=["health"])
    def liveness() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=settings.app_name,
            version=settings.service_version,
            environment=settings.environment,
        )

    @app.get("/health/ready", response_model=HealthResponse, tags=["health"])
    def readiness() -> HealthResponse:
        checks = service.readiness_checks()
        status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
        return HealthResponse(
            status=status,
            service=settings.app_name,
            version=settings.service_version,
            environment=settings.environment,
            checks=checks,
        )

    @app.post(
        f"{settings.api_prefix}/leads/evaluate",
        response_model=WorkflowResponse,
        tags=["revenue-ops"],
    )
    def evaluate_lead(
        body: LeadEvaluationRequest,
        request: Request,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> WorkflowResponse:
        return service.process(
            body,
            correlation_id=request.state.correlation_id,
            idempotency_key=idempotency_key,
        )

    app.include_router(workflow_router)
    return app


app = create_app()
