from .init_sys import init

init()

import cv2
import numpy as np
import os
from detect_models.get_detect_model import get_model
import logging
from works.celery_app import celery_app
from works.rabbitmq_channel import publish_rabbitmq_event

model = get_model('PredictCarNo')
logger = logging.getLogger(__name__)

# 定義 Celery 任務
@celery_app.task()
def detect_car_no_img(
    image_data, 
    message_id,
    millisecondsSinceEpoch, 
    path_to_save,
    no,
    camera_name,
    timestamp,
    line_name,
    ):
    def try_get_position(no:str):
        parts = no.split(".")
        if len(parts) > -1:
            return parts[-1]
        return None

    try:        
        readable_timestamp = millisecondsSinceEpoch
        # 將位元組數組轉換為圖像
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print(f"解碼圖像失敗，消息 ID 為 {message_id}")
            logger.error(f"解碼圖像失敗，消息 ID 為 {message_id}")
            return

        save_dir = os.path.join(path_to_save, f'{message_id}')

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        result,img,car_no = model.detect(img)
        position = try_get_position(no)
        
        event_data = {
            "occur_time": timestamp,
            "car_no": car_no if result else str("無"),
            "position": "車牌" if position is None else "前" if position == "1" else "後",
            "lane_name": line_name if line_name is not None else "無",
            "camera_name": camera_name,
            "no": no
            }
        
        publish_rabbitmq_event(event_data, 'car_no_detection_queue')

        if result is None:
            print(f"未能檢測到圖像中的車牌，消息 ID 為 {message_id}")
            logger.error(f"未能檢測到圖像中的車牌，消息 ID 為 {message_id}")
        elif result == True:
            print(f"在圖像中檢測到車牌，車號為 {car_no}，消息 ID 為 {message_id}")
            logger.info(f"在圖像中檢測到車牌，車號為 {car_no}，消息 ID 為 {message_id}")
        else:
            print(f"未找到圖像中的車牌，消息 ID 為 {message_id}")
            logger.info(f"未找到圖像中的車牌，消息 ID 為 {message_id}")

    except Exception as e:
        print(f"處理圖像時發生錯誤，消息 ID 為 {message_id}: {e}")
        logger.error(f"處理圖像時發生錯誤，消息 ID 為 {message_id}: {e}")