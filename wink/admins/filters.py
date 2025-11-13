"""
wink/admins/filters.py
"""

from wagtail.admin.filters import WagtailFilterSet


from wink.models_wink.comments import IntermediateCommentModel, CommentsModel
from wink.models_wink.files import IntermediateFilesModel, FilesModel

#
# IntermediateCommentModel
# IntermediateFilesModel
# CommentsModel
# FilesModel


class FilesFilter(WagtailFilterSet):
    class Meta:
        model = FilesModel
        fields = ["name", "size"]


class IntermediateFilesAdmin(WagtailFilterSet):
    class Meta:
        model = IntermediateFilesModel
        fields = [
            "upload_ai",
            "created_at",
            "updated_at",
            "status_file",
        ]
