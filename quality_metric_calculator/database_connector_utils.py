import logging

from quality_metric_calculator.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)
database_connector = DatabaseConnector()


def ensure_db_connection() -> None:
    if not database_connector.is_connected:
        logger.info("DB connector is disconnected, reconnecting")
        database_connector.connect()
