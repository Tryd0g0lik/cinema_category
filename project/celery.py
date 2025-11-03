import os
from celery import Celery
from celery.schedules import crontab
from project import celeryconfig

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
app = Celery(
    __name__,
    include=[
        "wink.tasks.task_start_rotation",
    ],
)
app.config_from_object(celeryconfig)
