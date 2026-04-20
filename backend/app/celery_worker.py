from celery import Celery
from app.config import settings

# Initialize Celery app connected to our Redis instance
celery_app = Celery(
    "tablewise_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery to use JSON securely
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Nairobi",
    enable_utc=True,
    broker_connection_retry_on_startup=True
)