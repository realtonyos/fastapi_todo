from celery import Celery

from app.core.config import settings

celery = Celery(
    "app.celery",  # обычно по имени модуля
    broker=settings.REDIS_URL,  # куда класть задачи
    backend=settings.REDIS_URL,   # куда класть результаты
    include=['app.celery.email']   # or autodiscover_tasks / где искать
)


celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=60
)
