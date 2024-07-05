from celery import Celery
from manager.thing_predict_log import ThingPredictLogManager
from setting.config import get_settings
import cv2
import numpy as np
import os
from kombu import Exchange, Queue
from detect_models.get_detect_model import get_model
import logging
import asyncio

thing_model = get_model('PredictThing')
thingPredictLogManager = ThingPredictLogManager()

settings = get_settings()

logger = logging.getLogger(__name__)

# 創建 Celery 實例並配置使用 Redis 作為 broker 和 backend
celery_app = Celery(
    'worker',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
        task_serializer='pickle',
        result_serializer='pickle',
        accept_content=['json', 'pickle'],
        timezone='UTC',
        enable_utc=True,
        task_ignore_result=True,  # 全局禁用任务结果存储
        task_track_started=False,  # 禁用任务状态跟踪
        result_expires=1,
        worker_max_tasks_per_child=20,
    )

celery_app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-length': 30}),
)

celery_app.conf.task_default_queue = 'default'
celery_app.conf.task_default_exchange = 'default'
celery_app.conf.task_default_routing_key = 'default'

# 定義 Celery 任務
@celery_app.task
def write_img(
    image_data, 
    message_id,
    millisecondsSinceEpoch, 
    path_to_save,
    no,
    timestamp,
    line_id,
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
            print(f"Failed to decode image for message ID {message_id}")
            logger.error(f"Failed to decode image for message ID {message_id}")
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

        if result is None:
            print(f"Failed to detect things in image for message ID {message_id}")
            logger.error(f"Failed to detect things in image for message ID {message_id}")
            return
        elif result == True:
            asyncio.run(thingPredictLogManager.create(
                occur_time = timestamp,
                thing_data = str(result),
                position = "車牌" if position is None else "前" if position == "1" else "後",
                lane_id = line_id
            ))
            print(f"Detected {len(result)} things in image for message ID {message_id}")
            logger.info(f"Detected {len(result)} things in image for message ID {message_id}")
        else:
            print(f"Not found to detect things in image for message ID {message_id}")
            logger.info(f"Not found to detect things in image for message ID {message_id}")
            return

    except Exception as e:
        print(f"An error occurred while processing image for message ID {message_id}: {e}")
        logger.error(f"An error occurred while processing image for message ID {message_id}: {e}")