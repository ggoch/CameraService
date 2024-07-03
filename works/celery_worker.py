from celery import Celery
from setting.config import get_settings
import cv2
import numpy as np
import os
# from detect_models.get_detect_model import get_model

# thing_model = get_model('PredictThing')

settings = get_settings()

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
        result_expires=60,
    )

# 定義 Celery 任務
@celery_app.task
def write_img(image_data, message_id,millisecondsSinceEpoch, path_to_save):

    try:
        readable_timestamp = millisecondsSinceEpoch
        # 將位元組數組轉換為圖像
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print(f"Failed to decode image for message ID {message_id}")
            return

        save_dir = os.path.join(path_to_save, f'{message_id}')

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 儲存處理後的影像
        save_path = os.path.join(save_dir, f'processed_image_{readable_timestamp}.png')
        success = cv2.imwrite(save_path, img)

        # result = thing_model.detect(img)


        if success:
            print(f"Image saved successfully at {save_path}")
        else:
            print(f"Failed to save image at {save_path}")
    except Exception as e:
        print(f"An error occurred while processing image for message ID {message_id}: {e}")