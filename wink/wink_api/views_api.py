"""
wink/wink_api/views_api.py
"""

import asyncio
import logging
import types
from adrf import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions

from wink.wink_api.serialisers import IntermediateFilesSerializer, FilesSerializer
from wink.models_wink.files import (
    FilesModel,
    IntermediateFilesModel,
)


class FilesViewSet(viewsets.ModelViewSet):
    queryset = FilesModel.objects.all()
    serializer_class = FilesSerializer
    permission_classes = [permissions.AllowAny]


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]
