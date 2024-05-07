import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime
from typing import List, Optional
from subscriber import run_subscriber
from math import ceil

RABBITMQ_HOST = '77.238.108.86'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'gateway'
RABBITMQ_PASSWORD = 'Bgateway@1256'
RABBITMQ_VHOST = 'gateway'

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_subscriber())


# Connect to MongoDB
client = MongoClient(
    "mongodb://77.238.108.86:27000/log?retryWrites=true&w=majority")
db = client["logs"]
collection = db["requests_logs"]


@app.get("/items/")
def get_items(
    class_id: Optional[str] = None,
    status_code: Optional[int] = None,
    created_at_start: Optional[datetime] = None,
    created_at_end: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 1,
) -> List[dict]:

    query = {}

    if class_id:
        query["class_id"] = class_id
    if status_code:
        query["status_code"] = status_code
    if created_at_start and created_at_end:
        query["created_at"] = {
            "$gte": created_at_start, "$lte": created_at_end}
    elif created_at_start:
        query["created_at"] = {"$gte": created_at_start}
    elif created_at_end:
        query["created_at"] = {"$lte": created_at_end}

    total_count = collection.count_documents(query)
    total_pages = ceil(total_count / page_size)
    skip = (page - 1) * page_size
    items = list(collection.find(query).skip(skip).limit(page_size))
    result_data = []
    for item in items:
        item['_id'] = str(item['_id'])
        result_data.append(item)
    data = {
        "total_count": total_count,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size,
        "items": result_data
    }
    return JSONResponse(content=data, status_code=200)
