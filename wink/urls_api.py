"""
wink/urls_api.py
"""

from django.urls import (path, include)
from rest_framework import routers

from wink.wink_api.views_api import (
    FilesViewSet,
    IntermediateFilesViewSet
)
from wink.csrftoken import CSRFTokenView

router = routers.DefaultRouter()
router.register("files", FilesViewSet)
urlpatterns = [
    path("", include(router.urls), name="api_urls_wink"),
    path("csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
