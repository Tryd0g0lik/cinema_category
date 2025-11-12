"""
wink/urls_api.py
"""

from django.urls import path, include
from rest_framework import routers

from wink import views
from wink.wink_api.comments.views_comments import (
    CommentViewSet,
    IntermediateCommentViewSet,
)
from wink.wink_api.files.views_files_api import FilesViewSet
from wink.wink_api.files.views_intermediate_files_api import IntermediateFilesViewSet


from wink.csrftoken import CSRFTokenView
from wink.wink_api.files.views_ai_api import FileReadOnlyView, FileRecordOnlyView
from wink.wink_api.violations.views_violations_api import BasisViolationViewSet

router = routers.DefaultRouter()
router.register("files", FilesViewSet, basename="wink_files")
router.register("cinema", IntermediateFilesViewSet, basename="wink_cinema")
router.register("violations", BasisViolationViewSet, basename="wink_violation")
router.register("comments", CommentViewSet, basename="wink_comment")
router.register("recommend", IntermediateCommentViewSet, basename="wink_recommend")
# router.register("download", FileReadOnlyModel.as_view(), basename="wink_readonly_file")
urlpatterns = [
    path("", include(router.urls), name="api_urls_wink"),
    path("download/<str:refer>/", FileReadOnlyView.as_view(), name="wink_read_file"),
    path("record/", FileRecordOnlyView.as_view(), name="wink_record_file"),
    path("sse/<str:index>/", views.file_event_stream, name="sse_stream"),
    path("csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
