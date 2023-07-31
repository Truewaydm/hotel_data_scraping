from fastapi import APIRouter, HTTPException

from app.api.models.hotels import HotelModel
from app.test_runner.test_tripadvisor import test_tripadvisor_prices

app_tripadvisor = APIRouter()


@app_tripadvisor.post("/send",
                      tags=["Prices"],
                      description="Send data for test {hotel_name: date_list}")
def send_date_list(hotel_data: HotelModel):
    """
    Endpoint for sending a date_list and receiving a response.
    :param hotel_data: HotelModel
    {
    "hotel_name": "The Grosvenor Hotel",
    "dates": [
        {"date": "3"},
        {"date": "8"},
        {"date": "11"},
        {"date": "16"},
        {"date": "23"}
    ]
}
    :return: The generated response prices
    {
  "The Grosvenor Hotel": {
        "03.10.2023-04.10.2023": [
        {
            "Booking.com": "$86",
            "screenshot": "03.10.2023-04.10.2023.png"
        },
      ....
      ....
      ....
    ]
}
    """
    try:
        hotel_name = hotel_data.hotel_name
        dates = hotel_data.dates

        if not hotel_name or not dates:
            raise HTTPException(status_code=400, detail="Bad Request: Missing hotel_name or dates")

        if not isinstance(hotel_name, str) or not isinstance(dates, list) or not all(
                isinstance(item, dict) and "date" in item for item in dates):
            raise HTTPException(status_code=400, detail="Bad Request: Invalid hotel_name or dates format")

        for date_item in dates:
            date_value = date_item.get("date")
            if not isinstance(date_value, str) or not date_value.strip():
                raise HTTPException(status_code=400, detail="Bad Request: Invalid dates format")

        prices = test_tripadvisor_prices(hotel_name, dates)
        return prices

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
