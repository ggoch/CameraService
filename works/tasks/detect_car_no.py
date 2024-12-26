from .init_sys import init

init()

import cv2
import numpy as np
import os
from detect_models.get_detect_model import get_model
import logging
from works.celery_app import celery_app
from works.rabbitmq_channel import publish_rabbitmq_event
from datetime import datetime
from setting.config import get_settings

settings = get_settings()
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

        today = datetime.now()
        formatted_date = today.strftime("%Y-%m-%d")

        save_dir = os.path.join(path_to_save,"car_no",formatted_date,f'{message_id}')

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        result,result_img,car_no = model.detect(img,settings.save_image)
        position = try_get_position(no)

        if result is True and car_no is not None:
            event_data = {
            "occur_time": timestamp,
            "car_no": car_no if result else str("無"),
            "position": "車牌" if position is None else "前" if position == "1" else "後",
            "lane_name": line_name if line_name is not None else "無",
            "camera_name": camera_name,
            "no": no
            }
        
            publish_rabbitmq_event(event_data, 'car_no_detection_queue')

        if(result is not None and car_no is not None and settings.save_image is True):
            # 儲存處理後的影像
            datetime_object = datetime.strptime(timestamp, "%Y/%m/%d %p %I:%M:%S")

            # 將 datetime 格式化為 24 小時制
            formatted_datetime = datetime_object.strftime("%Y-%m-%d_%H-%M-%S")
            save_path = os.path.join(save_dir, f'car_no_{formatted_datetime}.png')
            origin_save_path = os.path.join(save_dir, f'car_no_origin_{formatted_datetime}.png')
            success = cv2.imwrite(save_path, result_img)
            cv2.imwrite(origin_save_path, img)

            if success:
                print(f"Image saved successfully at {save_path}")
            else:
                print(f"Failed to save image at {save_path}")


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