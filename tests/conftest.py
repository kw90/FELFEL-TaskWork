from datetime import date

import pytest

from quality_metric_calculator.database_connector import Curve

minutes_since_start = [
    0,
    1,
    2,
    3,
    4,
]
inventory_values = [
    0,
    1,
    3,
    2,
    0,
]
consumption_profile = [
    6.32560226810635e-08,
    0.00013504066308609328,
    0.00028036591546969357,
    0.0003789538314549567,
    6.32560226810635e-08,
]


@pytest.fixture
def inventory_curve():
    return Curve(
        product_name="test_product_1",
        week_start=date(2021, 1, 1),
        minutes_since_week_start=minutes_since_start,
        value_at_minute=inventory_values,
    )


@pytest.fixture
def consumption_profile_curve():
    return Curve(
        product_name="test_product_1",
        week_start=date(2021, 1, 1),
        minutes_since_week_start=minutes_since_start,
        value_at_minute=consumption_profile,
    )
