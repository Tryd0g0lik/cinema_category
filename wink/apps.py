from django.apps import AppConfig
from django.dispatch import Signal, receiver


signal = Signal()


class WinkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wink"
