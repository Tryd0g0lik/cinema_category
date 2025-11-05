import os
from celery import Celery
from project import celeryconfig

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
app = Celery(
    __name__,
    include=[
        "wink.tasks.task_start_rotation",
        "wink.tasks.task_file_reader",
    ],
)
app.config_from_object(celeryconfig)
