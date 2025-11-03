"""
project/urls_api.py
"""

from django.urls import path, include
from wink.urls_api import urlpatterns as wink_urls

urlpatterns = [
    path("wink/", include(wink_urls)),
]
