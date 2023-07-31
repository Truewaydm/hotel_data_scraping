import json

import pytest

from app.test_runner.get_prices import find_hotel_prices
from app.test_runner.test_base import init_driver, close_driver
from app.test_runner.utils import get_file_path


@pytest.mark.parametrize(
    "hotel_name, dates",
    [
        ("The Grosvenor Hotel", [
            {"date": "3"},
            {"date": "8"},
            {"date": "11"},
            {"date": "16"},
            {"date": "23"},
        ]),
    ],
)
def test_tripadvisor_prices(hotel_name, dates):
    driver = init_driver()
    prices = find_hotel_prices(driver, hotel_name, dates)
    close_driver(driver)

    json_data = {hotel_name: prices}
    with open(get_file_path("json_data", "prices.json"), "w") as file:
        json.dump(json_data, file)
    return json_data
