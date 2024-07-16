from works.celery_app import celery_app as current_app

# 這確保了 Celery 應用程序在啟動時被正確加載
__all__ = ('current_app',)

current_app.autodiscover_tasks(['works.tasks'])

