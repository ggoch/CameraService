import aio_pika
import json
import logging
import asyncio
from rabbitmq.channel import get_rabbitmq_channel
from manager.thing_predict_log import ThingPredictLogManager
from manager.car_no_predict_log import CarNoPredictLogManager
from datetime import datetime

thingPredictLogManager = ThingPredictLogManager()
carNoPredictLogManager = CarNoPredictLogManager()

logger = logging.getLogger(__name__)

async def create_thing_predict_log(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            event_data = json.loads(message.body)
            occur_time = event_data.get('occur_time')
            line_name = event_data.get('line_name')
            camera_name = event_data.get('camera_name')
            no = event_data.get('no')
            position = event_data.get('position')
            thing_data = event_data.get('thing_data')

            time_format = '%Y/%m/%d %p %I:%M:%S'
            occur_time = datetime.strptime(occur_time, time_format)

            await thingPredictLogManager.create(
                occur_time=occur_time,
                thing_data=thing_data,
                position=position,
                lane_name=line_name,
                camera_name=camera_name,
                no=no
            )
        except Exception as e:
            print(f"Failed to process message: {e}")
            logger.error(f"Failed to process message: {e}")

async def create_car_no_predict_log(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            event_data = json.loads(message.body)
            occur_time = event_data.get('occur_time')
            line_name = event_data.get('line_name')
            camera_name = event_data.get('camera_name')
            no = event_data.get('no')
            position = event_data.get('position')
            car_no = event_data.get('car_no')

            time_format = '%Y/%m/%d %p %I:%M:%S'
            occur_time = datetime.strptime(occur_time, time_format)

            await carNoPredictLogManager.create(
                occur_time=occur_time,
                car_no=car_no,
                position="車牌" if position is None else "前" if position == "1" else "後",
                lane_name=line_name,
                camera_name=camera_name,
                no=no
            )
        except Exception as e:
            print(f"Failed to process message: {e}")
            logger.error(f"Failed to process message: {e}")

async def start_consuming(queue_name, callback):
    while True:
        try:
            channel = await get_rabbitmq_channel()
            queue = await channel.declare_queue(queue_name, durable=True)

            # 设置消费回调函数
            await queue.consume(callback)

            print(f'Waiting for messages in {queue_name}. To exit press CTRL+C')
            logger.info(f'Waiting for messages in {queue_name}. To exit press CTRL+C')
            await asyncio.Future()  # 保持事件循环运行

        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}, retrying in 5 seconds...")
            logger.error(f"Connection failed: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)  # 等待 5 秒后重试
        except Exception as e:
            print(f"Failed to start consuming: {e}")
            logger.error(f"Failed to start consuming: {e}")
            await asyncio.sleep(1)