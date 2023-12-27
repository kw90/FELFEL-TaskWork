from datetime import date, datetime, time
from unittest.mock import MagicMock, patch

import numpy as np

from quality_metric_calculator.database_connector import Curve, DatabaseConnector
from quality_metric_calculator.qos_calculator import (
    _calculate_availability,
    _calculate_cumulative_consumption_profile,
    _create_interp_function_from_array,
    _generate_timestamps_range,
    _minutes_to_datetimes,
    cached_qos_metric_calculation,
)


def test_minutes_to_datetimes():
    week_start = date(2023, 1, 1)
    minutes = [0, 60 * 24 * 7]

    result = _minutes_to_datetimes(minutes, week_start)

    assert result == [datetime(2023, 1, 1, 0, 0), datetime(2023, 1, 8, 0, 0)]


def test_create_interp_function_from_array():
    values = [0, 10, 20]
    minutes_since_week_start = [0, 60 * 12, 60 * 24]
    week_start = date(2023, 1, 1)

    f_interp = _create_interp_function_from_array(values, minutes_since_week_start, week_start)

    f_dt = datetime.combine(week_start, time(hour=6))
    assert f_interp(f_dt.timestamp()) == 5


def test_calculate_availability(inventory_curve):
    inventory_curves = [inventory_curve, inventory_curve]
    timestamps_range = _generate_timestamps_range(inventory_curves[0], range_in_minutes=5)

    result = _calculate_availability(inventory_curves, timestamps_range)

    assert result == {1609459200.0: 0.0, 1609459260.0: 1.0, 1609459320.0: 1.0, 1609459380.0: 1.0, 1609459440.0: 0.0}


def test_calculate_cumulative_consumption_profile():
    consumption_profile_curve = Curve(
        product_name="test_product_2",
        week_start=date(2023, 1, 1),
        minutes_since_week_start=[0, 60 * 12, 60 * 24],
        value_at_minute=[0, 10, 20],
    )
    timestamps_range = _generate_timestamps_range(consumption_profile_curve, range_in_minutes=5)
    result = _calculate_cumulative_consumption_profile(consumption_profile_curve, timestamps_range)
    print(result)
    np.testing.assert_allclose(result, [0.0, 0.1, 0.3, 0.6, 1.0])


@patch.object(DatabaseConnector, "get_inventory_curves")
@patch.object(DatabaseConnector, "get_consumption_profile_curves")
def test_cached_qos_metric_calculation(
    get_inventory_curves, get_consumption_profile_curves, inventory_curve, consumption_profile_curve
):
    database_connector = MagicMock()
    location = "TestLocation"
    week_str = "26.12.2020"
    expected_qos_metric = 1.0
    get_inventory_curves.return_value = [inventory_curve]
    get_consumption_profile_curves.return_value = [consumption_profile_curve]

    result = cached_qos_metric_calculation(location, week_str)

    assert result == expected_qos_metric
