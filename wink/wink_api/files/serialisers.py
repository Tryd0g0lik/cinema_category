"""
wink/wink_api/serialisers.py
"""

from adrf import serializers
from wink.models_wink.files import IntermediateFilesModel, FilesModel


class IntermediateFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntermediateFilesModel
        fields = "__all__"
        read_only_fields = ("created_at",)

    # def get_date_field(self, obj):
    #     if obj.datetime_field:
    #         return obj.datetime_field.date()
    #     return None


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilesModel
        fields = "__all__"
        read_only_fields = ("created_at",)
