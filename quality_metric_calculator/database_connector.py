import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import psycopg
from psycopg import OperationalError, sql

from quality_metric_calculator.settings import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

logger = logging.getLogger(__name__)


@dataclass
class Curve:
    product_name: str
    week_start: datetime
    minutes_since_week_start: list[int]
    value_at_minute: list[float]


class DatabaseConnector:
    def __init__(
        self,
    ):
        self.connection: Optional[psycopg.Connection] = None

    @property
    def is_connected(self) -> bool:
        if self.connection is None:
            return False
        return not self.connection.closed

    @property
    def is_healthy(self) -> bool:
        try:
            if self.connection is None or self.connection.closed:
                return False

            self.connection.execute("SELECT 1")
        except Exception:
            return False

        return True

    def get_inventory_curves(self, location: str, week: Optional[str] = None) -> list[Curve]:
        return self._get_curves("inventory_curve_id", location, week)

    def get_consumption_profile_curves(self, location: str, week: Optional[str] = None) -> list[Curve]:
        return self._get_curves("consumption_profile_curve_id", location, week)

    def insert_qos_metric(self, location: str, week: str, qos_metric: float) -> bool:
        week_date = datetime.strptime(week, "%d.%m.%Y").date()
        try:
            query = sql.SQL(
                "INSERT INTO public.qos_metrics (location, week_start, qos_metric) "
                + "VALUES ({}, {}, {}) ON CONFLICT DO NOTHING;"
            ).format(sql.Literal(location), sql.Literal(week_date), sql.Literal(qos_metric))
            self._insert_into_database(query)
            return True
        except Exception as ex:
            logger.error("Exception while inserting QoS metric (%s: %s)", type(ex).__name__, str(ex).strip())
        return False

    def connect(self) -> None:
        try:
            if self.connection is not None:
                logger.info("Closing existing connection")
                self.connection.close()
                self.connection = None
        except Exception as ex:
            logger.error("Exception while closing connection (%s: %s)", type(ex).__name__, str(ex).strip())
            self.connection = None

        self.connection = psycopg.connect(
            dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT
        )
        assert self.connection and self.is_connected
        self.connection.autocommit = True
        logger.info("Connected to DB at %s", POSTGRES_HOST)

    def _get_curves(self, curve_type: str, location: str, week: Optional[str] = None) -> list[Curve]:
        query = sql.SQL(
            "SELECT DISTINCT p.product, c.week_start, c.x, c.y "
            + "FROM public.products AS p "
            + "INNER JOIN public.curves as c on {} = c.curve_id "
            + "WHERE p.location = {} "
        )
        curve_id_column = sql.Identifier("p", curve_type)
        curve_query = query.format(curve_id_column, location)
        if week:
            query += sql.SQL("AND c.week_start = {}").format(sql.Literal(week))
        return [Curve(*curve) for curve in self._get_results_from_database(curve_query)]

    def _insert_into_database(self, query: sql.Composed) -> None:
        try:
            if not self.is_connected:
                self.connect()

            if self.connection is None:
                logger.warning("Can't insert into DB - not connected")
                raise OperationalError()

            with self.connection.cursor() as cursor:
                cursor.execute(query)
        except Exception as ex:
            logger.error("Error while inserting into DB (%s: %s)", type(ex).__name__, ex)
            raise

    def _get_results_from_database(self, query: sql.Composed) -> list[dict]:
        try:
            if not self.is_connected:
                self.connect()

            if self.connection is None:
                logger.warning("Can't retrieve list from DB - not connected")
                raise OperationalError()

            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result: list[dict] = cursor.fetchall()
                return result
        except Exception as ex:
            logger.error("Error while reading from the DB (%s: %s)", type(ex).__name__, ex)
            raise
