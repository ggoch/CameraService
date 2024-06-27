import asyncio
import cv2
import numpy as np
# from redis import Redis
from redis.asyncio import Redis
import os
import datetime
from works.celery_worker import write_img

async def handle_image(redis_client: Redis,message_id,path_to_save = "./camera_save"):
    # 从 Redis Hash 中获取图像和附加信息
    image_data = await redis_client.hget(message_id, 'image')
    timestamp = await redis_client.hget(message_id, 'timestamp')
    millisecondsSinceEpoch = await redis_client.hget(message_id, 'millisecondsSinceEpoch')
    width = await redis_client.hget(message_id, 'width')
    height = await redis_client.hget(message_id, 'height')
    no = await redis_client.hget(message_id, 'no')
    displayName = await redis_client.hget(message_id, 'displayName')
    description = await redis_client.hget(message_id, 'description')
    laneId = await redis_client.hget(message_id, 'laneId')

    timestamp = timestamp.decode('utf-8') if timestamp else None
    millisecondsSinceEpoch = int(millisecondsSinceEpoch.decode('utf-8')) if millisecondsSinceEpoch else None
    width = int(width.decode('utf-8')) if width else None
    height = int(height.decode('utf-8')) if height else None
    no = no.decode('utf-8') if no else None
    displayName = displayName.decode('utf-8') if displayName else None
    description = description.decode('utf-8') if description else None
    laneId = laneId.decode('utf-8') if laneId else None

    # 將timestamp轉換為可讀的格式並作為檔案名稱的一部分
    # try:
    #     if '下午' in timestamp:
    #         timestamp = timestamp.replace('下午', 'PM')
    #     elif '上午' in timestamp:
    #         timestamp = timestamp.replace('上午', 'AM')

    #     readable_timestamp = datetime.datetime.strptime(timestamp, '%Y/%m/%d %p %I:%M:%S').strftime("%Y%m%d_%H%M%S")
    #     # readable_timestamp = datetime.datetime.fromisoformat(timestamp).strftime("%Y%m%d_%H%M%S")
    # except Exception as e:
    #     print(f"Failed to convert timestamp for message ID {message_id}: {e}")
    #     readable_timestamp = "unknown_time"
    readable_timestamp = millisecondsSinceEpoch

    write_img.delay(image_data, message_id,readable_timestamp,path_to_save)
    

    # # 將位元組數組轉換為圖像
    # nparr = np.frombuffer(image_data, np.uint8)
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # # 进行图像处理（模型推断、绘图等）TODO
    # # processed_img = process_with_model(img)

    # if img is None:
    #     print(f"Failed to decode image for message ID {message_id}")
    #     return
    
    # save_dir = os.path.join(path_to_save, f'{message_id}')
    # # save_dir = path_to_save
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)

    # # 儲存處理後的影像
    # save_path = os.path.join(save_dir, f'processed_image_{readable_timestamp}.png')
    # success = cv2.imwrite(save_path, img)

    # if success:
    #     print(f"Image saved successfully at {save_path}")
    # else:
    #     print(f"Failed to save image at {save_path}")

async def sub_camera_event(redis_client: Redis,channel_name:str="image_channel"):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            if message['type'] == 'message':
                message_id = message['data'].decode('utf-8')
                await handle_image(redis_client,message_id)
        # await asyncio.sleep(0.1)  # 短暂休眠以避免高 CPU 占用