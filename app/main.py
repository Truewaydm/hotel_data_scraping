from datetime import datetime

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request

from app.api.routes.api_tripadvisor import app_tripadvisor

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
