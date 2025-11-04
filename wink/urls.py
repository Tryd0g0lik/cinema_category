"""
wink/urls.py
"""
from django.urls import path
from wink.views import main
urlpatterns = [
    path("admin/", main),
]
