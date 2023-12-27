import logging
from datetime import date, datetime, timedelta
from functools import lru_cache

import numpy as np
from scipy.interpolate import interp1d

from quality_metric_calculator.database_connector import Curve
from quality_metric_calculator.database_connector_utils import database_connector

MINUTES_IN_A_WEEK = 7 * 24 * 60


logger = logging.getLogger(__name__)


def _minutes_to_datetimes(minutes: list[int], week_start: date) -> list[datetime]:
    week_start_datetime = datetime.combine(week_start, datetime.min.time())
    return [week_start_datetime + timedelta(minutes=int(minute)) for minute in minutes]


def _create_interp_function_from_array(
    values: list[float], minutes_since_week_start: list[int], week_start: date, kind: str = "linear"
):
    datetimes = _minutes_to_datetimes(minutes_since_week_start, week_start)
    timestamps = [dt.timestamp() for dt in datetimes]
    return interp1d(timestamps, values, kind=kind, bounds_error=False, fill_value=0.0)


def _create_interp_function(curve: Curve, kind="linear"):
    return _create_interp_function_from_array(
        curve.value_at_minute, curve.minutes_since_week_start, curve.week_start, kind=kind
    )


def _generate_timestamps_range(curve: Curve, range_in_minutes: int = MINUTES_IN_A_WEEK) -> list[float]:
    start_datetime = datetime.combine(curve.week_start, datetime.min.time())
    end_datetime = start_datetime + timedelta(minutes=range_in_minutes)
    return [
        start_datetime.timestamp() + i * 60 for i in range(int((end_datetime - start_datetime).total_seconds() // 60))
    ]


def _calculate_availability(inventory_curves, timestamps):
    availability_counts, total_product_counts = {}, {}
    for curve in inventory_curves:
        f_inventory = _create_interp_function(curve)
        for timestamp in timestamps:
            inventory_level = f_inventory(timestamp)
            if timestamp not in availability_counts:
                availability_counts[timestamp] = 0
                total_product_counts[timestamp] = 0
            if inventory_level > 0:
                availability_counts[timestamp] += 1
            total_product_counts[timestamp] += 1
    return {ts: availability_count / total_product_counts[ts] for ts, availability_count in availability_counts.items()}


def _calculate_cumulative_consumption_profile(consumption_profile_curve: Curve, timestamps: list[float]) -> np.ndarray:
    f_consumption_profile = _create_interp_function(consumption_profile_curve)
    consumption_profile_values = [f_consumption_profile(ts) for ts in timestamps]
    total_consumption = sum(consumption_profile_values)
    cumulative_consumption = np.cumsum(consumption_profile_values)
    return np.divide(cumulative_consumption, total_consumption)


def _calculate_qos_metric(inventory_curves: list[Curve], consumption_profile_curves: list[Curve]) -> float:
    timestamps_range = _generate_timestamps_range(inventory_curves[0])
    availability_ratios = _calculate_availability(inventory_curves, timestamps_range)
    consumption_profile_curve = consumption_profile_curves[0]
    consumption_profile_cumulative = _calculate_cumulative_consumption_profile(
        consumption_profile_curve, timestamps_range
    )
    availability_interp_func = interp1d(
        timestamps_range, list(availability_ratios.values()), bounds_error=False, fill_value="extrapolate"
    )
    product_availability_ratio = availability_interp_func(timestamps_range)
    return np.trapz(product_availability_ratio, consumption_profile_cumulative)


@lru_cache(maxsize=128)
def cached_qos_metric_calculation(location: str, week_str: str) -> float:
    inventory_curves = database_connector.get_inventory_curves(location, week_str)
    consumption_profile_curves = database_connector.get_consumption_profile_curves(location, week_str)
    if not inventory_curves or not consumption_profile_curves:
        raise ValueError("No data found for the specified location and week combination.")
    return _calculate_qos_metric(inventory_curves, consumption_profile_curves)
