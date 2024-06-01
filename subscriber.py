import aio_pika
import pymongo
import json
from time import sleep
from dotenv import load_dotenv
import os

async def consume_message_from_rabbitmq():
    
    load_dotenv()
    rabbit_host = str(os.getenv("RABBITMQ_HOST"))
    rabbit_port = int(os.getenv("RABBITMQ_PORT"))
    rabbit_user = str(os.getenv("RABBITMQ_USERNAME"))
    rabbit_pass = str(os.getenv("RABBITMQ_PASSWORD"))
    rabbit_vhost = str(os.getenv("RABBITMQ_VHOST"))
    mongo_url = str(os.getenv("MONGO_URL"))
    exchange_name = str(os.getenv("RABBIT_EXCHANGE_NAME"))
    while(True):
        try:
            connection = await aio_pika.connect_robust(
                host=rabbit_host,
                port=rabbit_port,
                login=rabbit_user,
                password=rabbit_pass,
                virtualhost=rabbit_vhost
            )

            async with connection:
                channel = await connection.channel()

                # Declare a fanout exchange
                exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.FANOUT)

                # Declare a queue
                queue = await channel.declare_queue()

                # Bind the queue to the exchange
                await queue.bind(exchange)

                async for message in queue:
                    async with message.process():
                        try:
                            data = json.loads(message.body.decode())

                            class_id = 100
                            if data['status_code'] == 401:
                                if "admin" in data['request']['url'] or "Admin" in data['request']['url']:
                                    class_id = 1
                            elif data['status_code'] == 500:
                                class_id = 1
                            elif data['status_code'] == 400:
                                class_id = 1
                            elif data['status_code'] == 422:
                                class_id = 1

                            data['class'] = class_id
                            client = pymongo.MongoClient(
                                mongo_url)
                            db = client["logs"]
                            collection = db["requests_logs"]
                            result = collection.insert_one(data)
                            client.close()
                        except Exception as ex:
                            print(f"mongodb insertion faild with error : {ex}")

        except Exception as e:
            print(e)
        sleep(120)

# Run the subscriber coroutine
async def run_subscriber():
    await consume_message_from_rabbitmq()
