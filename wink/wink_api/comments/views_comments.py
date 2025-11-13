"""
wink/wink_api/violations/views_violations_api.py
"""

from wink.models_wink.comments import CommentsModel, IntermediateCommentModel
from wink.wink_api.comments.serializers import (
    CommentSerializer,
    IntermediateCommentSerializer,
)
from adrf import viewsets
from rest_framework import permissions


class CommentViewSet(viewsets.ModelViewSet):
    queryset = CommentsModel.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]


class IntermediateCommentViewSet(viewsets.ModelViewSet):
    queryset = IntermediateCommentModel.objects.all()
    serializer_class = IntermediateCommentSerializer
    permission_classes = [permissions.AllowAny]
