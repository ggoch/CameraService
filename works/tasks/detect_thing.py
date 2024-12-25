from .init_sys import init

init()

import cv2
import numpy as np
import os
from detect_models.get_detect_model import get_model
import logging
from works.celery_app import celery_app
from works.rabbitmq_channel import publish_rabbitmq_event


thing_model = get_model('PredictThing')
logger = logging.getLogger(__name__)

# 定義 Celery 任務
@celery_app.task
def detect_thing_img(
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

        # 儲存處理後的影像
        # print(f'processed_image_{readable_timestamp}.png')
        # save_path = os.path.join(save_dir, f'processed_image_{readable_timestamp}.png')
        # success = cv2.imwrite(save_path, img)



        # if success:
        #     print(f"Image saved successfully at {save_path}")
        # else:
        #     print(f"Failed to save image at {save_path}")

        result = thing_model.detect(img)
        position = try_get_position(no)

        event_data = {
            "occur_time": timestamp,
            "thing_data": str("E006") if result is True else str("無"),
            "position": "車牌" if position is None else "前" if position == "1" else "後",
            "lane_name": line_name if line_name is not None else "無",
            "camera_name": camera_name,
            "no": no
            }
        
        publish_rabbitmq_event(event_data, 'thing_detection_queue')

        if result is None:
            print(f"未能檢測到圖像中的物料，消息 ID 為 {message_id}")
            logger.error(f"未能檢測到圖像中的物料，消息 ID 為 {message_id}")
        elif result == True:
            print(f"在圖像中檢測到物料，消息 ID 為 {message_id}")
            logger.info(f"在圖像中檢測到物料，消息 ID 為 {message_id}")
        else:
            print(f"未找到圖像中的物料，消息 ID 為 {message_id}")
            logger.info(f"未找到圖像中的物料，消息 ID 為 {message_id}")

    except Exception as e:
        print(f"處理圖像時發生錯誤，消息 ID 為 {message_id}: {e}")
        logger.error(f"處理圖像時發生錯誤，消息 ID 為 {message_id}: {e}")