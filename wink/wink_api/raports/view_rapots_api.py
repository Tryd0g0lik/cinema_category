import os
import asyncio
import logging
import datetime
import threading
from adrf import views
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from logs import configure_logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
