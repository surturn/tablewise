from celery import Celery
from app.config import settings

celery_app = Celery("grandplatform_tasks", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Juba",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_routes={
        "app.tasks.send_sms_notification": {"queue": "sms"},
        "app.tasks.send_email": {"queue": "sms"},
        "app.tasks.generate_inventory_forecast": {"queue": "ai_tasks"},
        "app.tasks.deduct_inventory": {"queue": "default"},
        "app.tasks.schedule_housekeeping": {"queue": "default"},
    },
    task_queue_max_priority={"sms": 10, "default": 5, "ai_tasks": 1},
)
