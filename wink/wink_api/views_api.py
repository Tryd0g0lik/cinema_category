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
    # parser_classes = (MultiPartParser, FormParser)

    async def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid()
        if not is_valid:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        await serializer.asave()
        data = serializer.data
        try:
            f = await asyncio.to_thread(lambda: self.queryset.get(pk=data.get("id")))
            await asyncio.to_thread(
                lambda: IntermediateFilesModel.objects.create(user=user, upload=f)
            )
        except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_201_CREATED)


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]


# запустить celery
# сделать refer  а парсинг
# сдулать удаление только для продусера и админа
# Сделать роутер к базе данных
