from pydantic import BaseModel


class HotelModel(BaseModel):
    hotel_name: str
    dates: list[dict[str, str]]
