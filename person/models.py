"""
person/models.py
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserModel(AbstractUser):
    id = models.BigAutoField(primary_key=True)
