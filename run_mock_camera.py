import asyncio
import datetime
import cv2
import redis.asyncio as redis

import argparse
import os
from dotenv import load_dotenv
import logging
import sys

log_dir = "logs"  # 專案內的 logs 資料夾
log_file = os.path.join(log_dir, "mock_camera.log")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

async def get_current_timestamp():
    now = datetime.datetime.now()
    formatted_time = now.strftime('%Y/%m/%d %p %I:%M:%S')
    if 'AM' in formatted_time:
        formatted_time = formatted_time.replace('AM', '上午')
    elif 'PM' in formatted_time:
        formatted_time = formatted_time.replace('PM', '下午')
    return formatted_time

async def read_image_data(file_path):
    # 使用 cv2 讀取圖片
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"The file at {file_path} does not exist or is not a valid image.")
    
    # 將圖片轉換為二進制數據
    _, img_encoded = cv2.imencode('.png', img)
    return img_encoded.tobytes()

async def set_hash_data(redis_client, key, file_path):
    timestamp = await get_current_timestamp()
    image_data = await read_image_data(file_path)

    await redis_client.hset(key, mapping={
        'image': image_data,
        'timestamp': timestamp,
        'millisecondsSinceEpoch': "1620000000000",
        'width': str(1280),  # 記得將整數轉換為字符串
        'height': str(720),  # 記得將整數轉換為字符串
        'no': "1.3",
        'displayName': "測試攝影機",
        'description': "測試攝影機",
        'laneId': ""
    })

async def publish_and_update(redis_client, channel, key, settings):    
    while True:
        # 更新特定的 key
        await set_hash_data(redis_client, key, settings.mock_img_path)
        print(f"Updated key {key}")
        logger.info(f"Updated key {key}")

        # 發佈事件
        await redis_client.publish(channel, key)
        print(f"Published message to {channel}: {key}")
        logger.info(f"Published message to {channel}: {key}")

        # 每 5 秒執行一次
        await asyncio.sleep(settings.mock_publish_seconds)

async def main():
    from database.redis_cache import not_decode_redis_pool
    from setting.config import get_settings

    settings = get_settings()

    # 連接到 Redis
    redis_client = redis.Redis(connection_pool=not_decode_redis_pool)
    
    try:
        # 設置頻道和 key
        channel = 'image_channel'
        key = 'test_key'

        # 開始發佈和更新
        await publish_and_update(redis_client, channel, key, settings)
    finally:
        redis_client.close()
        await redis_client.wait_closed()

# 啟動
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    parser.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    parser.add_argument("--test",action="store_true", help="Run the server in test mode.")
    parser.add_argument("--dev",action="store_true", help="Run the server in development mode.")
    
    db_type =  parser.add_argument_group(title="Database Type", description="Run the server in different database type.")
    db_type.add_argument("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")

    run_mode = parser.add_argument_group(title="Run Mode", description="Run the server in Async or Sync mode. Default is Async.")
    run_mode.add_argument("--sync",action="store_true", help="Run the server in Sync mode.")

    args = parser.parse_args()

    if args.prod:
        load_dotenv("setting/.env.prod")
    elif args.test:
        load_dotenv("setting/.env.test")
    else:
        load_dotenv("setting/.env.dev")

    if args.sync:
        os.environ["RUN_MODE"] = "SYNC"
    else:
        os.environ["RUN_MODE"] = "ASYNC"

    os.environ["DB_TYPE"] = args.db

    asyncio.run(main())