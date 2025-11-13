from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from wink.admins.filters import FilesFilter, IntermediateFilesAdmin
from wink.models_wink.comments import CommentsModel
from wink.wink_api.files.views_ai_api import (
    IntermediateFilesModel,
    FilesModel,
)


class BasicAdmin(SnippetViewSet):
    list_per_page = 20


# ======================================================
# ---------------- FILES -------------------------------
# ======================================================
class FilesAdmin(BasicAdmin):
    model = FilesModel
    list_display = ["name", "size", "id"]
    list_filter = ["name", "size"]
    search_fields = ["name"]
    ordering = ["name", "size"]
    filterset_class = FilesFilter


register_snippet(FilesAdmin)


class IntermediateFilesAdmin(BasicAdmin):
    model = IntermediateFilesModel
    menu_label = _("Comments")
    icon = "comment"
    list_display = [
        "upload",
        "upload_ai",
        "user",
        "created_at",
        "updated_at",
        "status_file",
        "id",
    ]
    list_filter = [
        "upload_ai",
        "created_at",
        "updated_at",
        "status_file",
    ]
    search_fields = [
        "upload_ai",
        "created_at",
        "updated_at",
        "status_file",
    ]
    ordering = [
        "upload_ai",
        "created_at",
        "updated_at",
        "status_file",
    ]
    filterset_class = IntermediateFilesAdmin
    readonly_fields = ["upload_ai", "created_at", "status_file", "id"]


register_snippet(IntermediateFilesAdmin)


# ======================================================
# ---------------- COMMENTS ----------------------------
# ======================================================
class CommentsAdmin(BasicAdmin):
    model = CommentsModel
    menu_label = _("Comments")
    icon = "comment"  # Иконка для меню
    list_display = [
        "comment_author",
        "comment",
        "created_at",
        "updated_at",
        "id",
    ]

    list_filter = ["comment_author", "created_at", "updated_at"]
    search_fields = ["comment_author", "comment", "created_at", "updated_at"]
    ordering = ["comment_author", "created_at", "updated_at"]
    readonle_filds = ["comment_author", "created_at", "id"]

    def get_queryset(self, request):
        return super().get_queryset(request)


register_snippet(CommentsAdmin)
