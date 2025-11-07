"""
wink/urls_api.py
"""

from django.urls import path, include
from rest_framework import routers

from wink.wink_api.files.views_files_api import FilesViewSet
from wink.wink_api.files.views_intermediate_files_api import IntermediateFilesViewSet


from wink.csrftoken import CSRFTokenView

router = routers.DefaultRouter()
router.register("files", FilesViewSet, basename="wink_files")
router.register("cinema", IntermediateFilesViewSet, basename="wink_cinema")
urlpatterns = [
    path("", include(router.urls), name="api_urls_wink"),
    path("csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
