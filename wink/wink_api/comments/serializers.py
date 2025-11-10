"""
wink/wink_api/violations/serializers.py
"""

from wink.models_wink.comments import CommentsModel, IntermediateCommentModel
from adrf import serializers


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentsModel
        fields = "__all__"


class IntermediateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntermediateCommentModel
        fields = "__all__"
