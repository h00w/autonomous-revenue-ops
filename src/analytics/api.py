from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from ..orchestration.runtime import get_workflow_store
from ..security.auth import require_workflow_api_key
from .models import BusinessImpactProjection, BusinessImpactScenario, OperationalSnapshot
from .prometheus import render_prometheus
from .service import AnalyticsService

router = APIRouter(
    prefix="/v1/analytics",
    tags=["analytics"],
    dependencies=[Depends(require_workflow_api_key)],
)


def _service() -> AnalyticsService:
    return AnalyticsService(get_workflow_store())


@router.get("/summary", response_model=OperationalSnapshot)
def operational_summary() -> OperationalSnapshot:
    return _service().snapshot()


@router.get("/metrics", response_class=PlainTextResponse)
def operational_metrics() -> str:
    return render_prometheus(_service().snapshot())


@router.post("/impact", response_model=BusinessImpactProjection)
def business_impact(body: BusinessImpactScenario) -> BusinessImpactProjection:
    return AnalyticsService.project_business_impact(body)
