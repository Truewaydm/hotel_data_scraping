from datetime import datetime

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from rq import Queue
from redis import Redis
from app.api.routes.api_tripadvisor import app_tripadvisor

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
