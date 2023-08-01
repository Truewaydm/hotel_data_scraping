# Test runner for RestAPI app

Test system flow with using Python, Appium
and Android simulator

## Prerequisites

- Python 3.10
- fastapi
- uvicorn
- pytest
- appium-python-client
- redis
- rq

## Usage 

### Getting Started
Clone this repository:

```bash
git clone git@github.com:Truewaydm/hotel_data_scraping.git
````

Install the dependencies:

```bash
pip install -r requirements.txt
 ````

Install Android Studio:

[Android Studio](https://developer.android.com/studio)

- Go to Virtual device manager and Run emulator

Install APK file in device emulator

- path: app/test_runner/apk/tripadvisor_53.4.apk
- Open tripadvisor app

Install Appium

[Appium Documentation](https://appium.io/docs/en/2.0/)

In terminal start appium
```
appium --allow-cors
```

Open inspector appiumpro

- [inspector appiumpro](https://inspector.appiumpro.com/)

Set dependencies to inspector appiumpro:
```
Remote Host: 127.0.0.1
Remote Port: 4723
Remote Path: /
Advanced Settings: Allow Unauthorized Certificates

Desired Capabilities
    'platformName': 'Android',
    'deviceName': 'emulator-5554',
    'appPackage': 'com.tripadvisor.tripadvisor',
    'appActivity': 'com.tripadvisor.tripadvisor.TripAdvisorTripAdvisorActivity',
    'noReset': True,
    'automationName': "UiAutomator2"
```

Install Redis Server
```
sudo apt install redis-server
```

In terminal start Redis Server
```
redis-server
```

In terminal start rq worker
```
rq worker
```

### Run


```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

For example:
```
Request:
curl --location 'http://localhost:3000/api/send' \
--header 'Content-Type: application/json' \
--data '{
    "hotel_name": "The Grosvenor Hotel",
    "dates": [
        {
            "date": "3"
        },
        {
            "date": "8"
        },
        {
            "date": "11"
        },
        {
            "date": "16"
        },
        {
            "date": "23"
        }
    ]
}'
---------------------------------------------------
Response:
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
    ],
  }
}
```

## Launching individual parts 1,2,3

Modify the code as needed to test different parts

### test_runner app
Part 1. Run test_runner 
```
# test_tripadvisor.py
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
```
### Usage RestAPI app
Part 2. Run RestAPI <---> test_runner
```
# main.py
app = FastAPI()

app.include_router(
    app_tripadvisor,
    prefix='/api',
)


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    execution_time = (datetime.utcnow() - start_time).microseconds
    response.headers["x-execution-time"] = str(execution_time)
    return response


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=3000, reload=True)
```
```
# api_tripadvisor.py
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
```

### Usage queue
Part 3. Run RestAPI <---> Queue <---> test_runner
```
# main.py
app = FastAPI()

redis_conn = Redis(host='localhost', port=6379)

queue = Queue(connection=redis_conn)

app.include_router(
    app_tripadvisor,
    prefix='/api'
)


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    execution_time = (datetime.utcnow() - start_time).microseconds
    response.headers["x-execution-time"] = str(execution_time)
    return response


@app.on_event("shutdown")
async def shutdown_event():
    redis_conn.close()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=3000, reload=True)
```
```
# api_tripadvisor.py
app_tripadvisor = APIRouter()

redis_conn = Redis(host='localhost', port=6379)

queue = Queue(connection=redis_conn)


@app_tripadvisor.post("/send",
                      tags=["Prices"],
                      description="Send data for test {hotel_name: date_list}")
async def send_date_list(hotel_data: HotelModel):
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

        job = queue.enqueue(test_tripadvisor_prices, hotel_name, dates)
        while not job.is_finished:
            time.sleep(5)
        job_result = job.return_value
        if isinstance(job_result, Exception):
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(job_result)}")

        with open(get_file_path("json_data", "prices.json"), "r") as file:
            json_data = json.load(file)
        return json_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
```
