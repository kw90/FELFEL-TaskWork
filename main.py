import logging

import uvicorn

from quality_metric_calculator.settings import UVICORN_HOST, UVICORN_PORT, UVICORN_RELOAD, UVICORN_WORKERS


# disable access log on /healthcheck
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    uvicorn.run(
        "quality_metric_calculator.api:fast_api",
        log_config=None,
        port=UVICORN_PORT,
        workers=UVICORN_WORKERS,
        host=UVICORN_HOST,
        reload=UVICORN_RELOAD,
    )


if __name__ == "__main__":
    main()
