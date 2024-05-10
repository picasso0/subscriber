import asyncio
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime
from typing import List, Optional
from subscriber import run_subscriber
from math import ceil
from dotenv import load_dotenv
import os

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
    classNumber: Optional[int] = None,
    statusCode: Optional[int] = None,
    page: int = 1,
    count: int = 10,
    authorization: str = Header(None)
) -> List[dict]:
    
    load_dotenv()
    correct_token = str(os.getenv("TOEKN"))
    if authorization is None or authorization != correct_token:
        raise HTTPException(status_code=401, detail="کاربر احراز هویت نشده است")

    query = {}

    if classNumber:
        query["class"] = classNumber
    if statusCode:
        query["status_code"] = statusCode
    total_count = collection.count_documents(query)
    total_pages = ceil(total_count / count)
    skip = (page - 1) * count
    items = list(collection.find(query).skip(skip).limit(count))
    result_data = []
    for item in items:
        item['_id'] = str(item['_id'])
        result_data.append(item)
    data = {
        "data":{
        "totalCount": total_count,
        "totalPages": total_pages,
        "currentPage": page,
        "count": count,
        "items": result_data
        },
        "message":"عملیات با موفقیت انجام شد",
        "id":4968,
        "code":200
    }
    return JSONResponse(content=data, status_code=200)
