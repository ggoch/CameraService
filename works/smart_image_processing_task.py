from celery import Task, Celery
from celery.utils.log import get_task_logger
import time
from collections import deque

logger = get_task_logger(__name__)

class SmartImageProcessingTask(Task):
    max_queue_size = 20
    _task_queue = deque(maxlen=max_queue_size)

    def apply_async(self, args=None, kwargs=None, **options):
        current_time = int(time.time())  # 取整數秒
        task_id = options.get('task_id', str(current_time))  # 使用自定義 task_id 或時間戳

        # 從 kwargs 中提取額外參數
        extra_params = kwargs.pop('extra_params', {}) if kwargs else {}
        
        # 檢查是否有相同 task_id 的任務
        same_task_index = next((i for i, task in enumerate(self._task_queue) 
                                if task['task_id'] == task_id), None)
        
        if same_task_index is not None:
            # 如果有相同 task_id 的任務，替換它
            logger.info(f"Replacing task with id {task_id}")
            self._task_queue[same_task_index] = {
                'time': current_time,
                'task_id': task_id,
                'args': args,
                'kwargs': kwargs,
                'options': options,
                'extra_params': extra_params
            }
        elif len(self._task_queue) < self.max_queue_size:
            # 如果隊列未滿，直接添加
            logger.info(f"Adding new task with id {task_id}")
            self._task_queue.append({
                'time': current_time,
                'task_id': task_id,
                'args': args,
                'kwargs': kwargs,
                'options': options,
                'extra_params': extra_params
            })
        else:
            # 隊列已滿，根據額外參數決定是否替換
            oldest_task = self._task_queue[0]
            if self.should_replace(oldest_task['extra_params'], extra_params):
                logger.info(f"Queue full, replacing oldest task with new task id {task_id}")
                self._task_queue.popleft()  # 移除最舊的任務
                self._task_queue.append({
                    'time': current_time,
                    'task_id': task_id,
                    'args': args,
                    'kwargs': kwargs,
                    'options': options,
                    'extra_params': extra_params
                })
            else:
                logger.info(f"Queue full, new task with id {task_id} not added")
                return None  # 不添加新任務

        # 實際執行任務
        return super().apply_async(args, kwargs, **options)

    def should_replace(self, old_params, new_params):
        # 這個方法決定是否應該替換任務
        # 您可以根據實際需求自定義這個方法
        return new_params.get('priority', 0) > old_params.get('priority', 0)

    def run(self, *args, **kwargs):
        # 這個方法將在子類中被覆蓋
        pass