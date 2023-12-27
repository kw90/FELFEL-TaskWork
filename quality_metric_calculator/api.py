import logging

from fastapi import APIRouter, Depends, FastAPI
from fastapi.exceptions import HTTPException

from quality_metric_calculator.database_connector_utils import database_connector, ensure_db_connection
from quality_metric_calculator.qos_calculator import cached_qos_metric_calculation

logger = logging.getLogger(__name__)
v1_router = APIRouter(prefix="/api/v1")
fast_api = FastAPI(title="QoS API")


@fast_api.on_event("shutdown")
async def on_shutdown() -> None:
    fast_api.state.executor.shutdown()


@fast_api.head("/healthcheck", responses={200: {"description": "ok"}, 500: {"description": "unhealthy"}})
@fast_api.get("/healthcheck", responses={200: {"description": "ok"}, 500: {"description": "unhealthy"}})
def healthcheck() -> str:
    """
    Checks whether the API is running correctly.
    Returns
    ---
        "ok" if the API is running correctly.
    """
    if not database_connector.is_healthy:
        database_connector.connect()
    if not database_connector.is_healthy:
        fast_api.state.executor.shutdown()
        raise HTTPException(status_code=500, detail="Database connection is unhealthy.")
    return "ok"


@v1_router.get(
    "/qos/{location}/week/{week_str}",
    dependencies=[Depends(ensure_db_connection)],
    responses={
        200: {
            "description": "The QoS metric for the specified location and week in ISO format.",
            "content": {"application/json": {"schema": {"example": {"Example AG": 0.95}}}},
        }
    },
)
def get_location_qos_metric_week(location: str, week_str: str) -> dict[str, float]:
    logger.info("Calculating QoS metric for %s", location)
    try:
        qos_metric = cached_qos_metric_calculation(location, week_str)
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        logger.error("Exception while calculating QoS metric for %s: %s", location, ex)
        raise HTTPException(status_code=500, detail=str(ex)) from ex
    logger.info("QoS metric for %s is %s", location, qos_metric)
    is_inserted = database_connector.insert_qos_metric(location, week_str, qos_metric)
    if is_inserted:
        logger.info("Inserted QoS metric for %s into database", location)
    else:
        logger.error("Failed to insert QoS metric for %s into database", location)
    return {location: qos_metric}


fast_api.include_router(v1_router)
