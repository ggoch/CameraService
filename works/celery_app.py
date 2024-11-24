from celery import Celery
from setting.config import get_settings

settings = get_settings()

# 創建 Celery 實例並配置使用 Redis 作為 broker 和 backend
celery_app = Celery(
    "worker", broker=settings.celery_broker_url, backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["json", "pickle"],
    timezone="UTC",
    enable_utc=True,
    task_ignore_result=True,  # 全局禁用任务结果存储
    task_track_started=False,  # 禁用任务状态跟踪
    result_expires=1,
    worker_max_tasks_per_child=10,
    worker_prefetch_multiplier=1,
    task_time_limit=60,  # 硬超時
    task_soft_time_limit=50,  # 軟超時
    # broker_transport_options={
    #     'queue_class': 'kombu.transport.redis.StreamQueue',
    #     'stream_max_length': 500,
    #     'stream_timeout': 10000,  # 10 秒，单位是毫秒
    #     'visibility_timeout': 5
    # },
)

# celery_app.conf.task_queues = (
#     Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-length': 30}),
# )

# celery_app.conf.task_default_queue = 'default'
# celery_app.conf.task_default_exchange = 'default'
# celery_app.conf.task_default_routing_key = 'default'

# celery_app.conf.task_cls = 'celery.contrib.abortable.AbortableAsyncTask'


celery_app.autodiscover_tasks(["works.tasks"])
