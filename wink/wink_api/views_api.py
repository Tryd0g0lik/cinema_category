"""
wink/wink_api/views_api.py
"""

import asyncio
import logging
import types
from adrf import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from wink.wink_api.serialisers import IntermediateFilesSerializer, FilesSerializer
from wink.models_wink.files import (
    FilesModel,
    IntermediateFilesModel,
)


class FilesViewSet(viewsets.ModelViewSet):
    queryset = FilesModel.objects.all()
    serializer_class = FilesSerializer
    permission_classes = [permissions.AllowAny]


    def create(self, request, *args, **kwargs):
        # response = super().create(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid()
        if not is_valid:
            pass
        else:
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]
