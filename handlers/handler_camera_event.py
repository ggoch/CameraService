import asyncio
import cv2
import numpy as np
# from redis import Redis
from redis.asyncio import Redis
import os
import datetime
from works.tasks import detect_thing_img,detect_car_no_img

laneMap = {
    '53230D8E-A654-EF99-5204-3A059359F294': '車道1',
    'AE291446-4980-9804-3579-3A059359F294': '車道2',
    '406FDF75-8739-8AD5-2047-3A059359F294': '車道3',
    'F1CE271B-0F96-7385-2D94-3A059359F294': '車道4',
    '4BA40A15-11F9-15C1-5CFE-3A059359F294': '車道5',
}

async def handle_image(redis_client: Redis,message_id,path_to_save = "./camera_save"):
    def try_get_position(no:str):
        parts = no.split(".")
        if len(parts) > -1:
            return parts[-1]
        return None
    
    # 从 Redis Hash 中获取图像和附加信息
    hash_data = await redis_client.hgetall(message_id)

    # 从hash_data中提取字段
    image_data = hash_data.get(b'image')
    timestamp = hash_data.get(b'timestamp').decode('utf-8')
    millisecondsSinceEpoch = hash_data.get(b'millisecondsSinceEpoch').decode('utf-8')
    width = int(hash_data.get(b'width').decode('utf-8'))
    height = int(hash_data.get(b'height').decode('utf-8'))
    no = hash_data.get(b'no').decode('utf-8')
    displayName = hash_data.get(b'displayName').decode('utf-8')
    description = hash_data.get(b'description').decode('utf-8')
    laneId = hash_data.get(b'laneId').decode('utf-8')

    # 將timestamp轉換為可讀的格式並作為檔案名稱的一部分
    try:
        if '下午' in timestamp:
            timestamp = timestamp.replace('下午', 'PM')
        elif '上午' in timestamp:
            timestamp = timestamp.replace('上午', 'AM')

        readable_timestamp = datetime.datetime.strptime(timestamp, '%Y/%m/%d %p %I:%M:%S').strftime("%Y%m%d_%H%M%S")
        # readable_timestamp = datetime.datetime.fromisoformat(timestamp).strftime("%Y%m%d_%H%M%S")
    except Exception as e:
        print(f"Failed to convert timestamp for message ID {message_id}: {e}")
        readable_timestamp = "unknown_time"
    readable_timestamp = millisecondsSinceEpoch

    position = try_get_position(no)

    if position is None:
        print(f"Failed to get position for message ID {message_id}")
        return
    
    if position == '1' or position == '2':
        detect_thing_img.apply_async(args=[
            image_data, 
            message_id,
            readable_timestamp,
            path_to_save,
            no,
            displayName,
            timestamp,
            laneMap.get(laneId),
            ],
            expires=2)
        
    if position == '3':
        detect_car_no_img.apply_async(args=[
            image_data, 
            message_id,
            readable_timestamp,
            path_to_save,
            no,
            displayName,
            timestamp,
            laneMap.get(laneId),
            ],
            expires=2)
    

async def sub_camera_event(redis_client: Redis,channel_name:str="image_channel"):
    while True:
        try:
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(channel_name)

            while True:
                try:
                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        if message['type'] == 'message':
                            message_id = message['data'].decode('utf-8')
                            await handle_image(redis_client, message_id)
                except Exception as e:
                    print(f"Error while processing message: {e}")
                    # logger
                await asyncio.sleep(0.1)  # 短暂休眠以避免高 CPU 占用
        except asyncio.CancelledError:
            # 清理工作
            print("Task was cancelled")
            raise
        except Exception as e:
            print(f"Redis connection error: {e}")
            # 重新连接前等待一段时间
            await asyncio.sleep(5)