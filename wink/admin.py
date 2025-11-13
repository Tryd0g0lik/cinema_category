from datetime import datetime
from django.utils.translation import gettext_lazy as _

# Register your models here.
from django.contrib import admin
from django.utils.formats import date_format
from wagtail.admin.panels import FieldPanel
from wagtail.admin.ui.tables import BaseColumn
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.ui.tables import UpdatedAtColumn

from wink.admins.filters import FilesFilter, IntermediateFilesAdmin
from wink.models_wink.comments import IntermediateCommentModel, CommentsModel

# from wink.models_wink.files import FilesModel
from wink.wink_api.files.views_ai_api import (
    FileRecordOnlyView,
    FileReadOnlyView,
    IntermediateFilesModel,
    FilesModel,
)
from wink.wink_api.files.views_files_api import FilesViewSet
from wink.wink_api.files.views_intermediate_files_api import IntermediateFilesViewSet
from wink.wink_api.violations.views_violations_api import BasisViolationViewSet


class BasicInline(admin.StackedInline):
    model = IntermediateFilesModel
    extra = 0
    ordering = ["refer"]
    fields = "__all__"


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
        "refer",
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
        "refer",
        "status_file",
    ]
    search_fields = [
        "upload_ai",
        "created_at",
        "updated_at",
        "refer",
        "status_file",
    ]
    ordering = [
        "upload_ai",
        "created_at",
        "updated_at",
        "status_file",
    ]
    filterset_class = IntermediateFilesAdmin
    readonly_fields = ["upload_ai", "created_at", "refer", "status_file", "id"]

    def get_refer_display(self, obj):
        return str(obj.refer)[:8] + "..."  # Показывать только первые 8 символов UUID

    get_refer_display.short_description = _("Reference")


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
        "refer",
        "created_at",
        "updated_at",
        "id",
    ]
    list_filter = ["comment_author", "refer", "created_at", "updated_at"]
    search_fields = ["comment_author", "comment", "refer", "created_at", "updated_at"]
    ordering = ["comment_author", "created_at", "updated_at"]
    readonle_filds = ["comment_author", "created_at", "id"]
    inlines = [BasicInline]

    def get_queryset(self, request):
        return super().get_queryset(request)


register_snippet(CommentsAdmin)
