"""
wink/wink_api/views_api.py
"""

import asyncio
import datetime
import logging
import threading
import os
from adrf import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from wink.wink_api.serialisers import IntermediateFilesSerializer, FilesSerializer
from wink.models_wink.files import (
    FilesModel,
    IntermediateFilesModel,
)
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


async def handle_uploaded_file(path, f):
    with open(path, "wb+") as destination:
        for chunk in f.chunks(10 * 1024 * 1024):
            destination.write(chunk)


class FilesViewSet(viewsets.ModelViewSet):
    queryset = FilesModel.objects.all()
    serializer_class = FilesSerializer
    permission_classes = [permissions.AllowAny]

    async def create(self, request, *args, **kwargs):

        error_text = "[%s.%s]:" % (
            __class__,
            __class__.__name__,
        )
        file = request.FILES["upload"]
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid()
        if not is_valid:
            log.error(
                "%s Error => %s",
                (
                    error_text,
                    "Request data is not valid.",
                ),
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # RECORD META DATA
            f_object = FilesModel(name=file.name, size=file.size, upload=None)
            await f_object.asave()

        except Exception as e:
            log.error(
                "%s Error => %s",
                (
                    error_text,
                    e.args[0],
                ),
            )
            return Response(
                {"error": f"{error_text}  Error =>  {e.args[0]}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Get path for file
            date = datetime.date.today().strftime("%Y-%m-%d").split("-")
            file_path = f"upload\\{date[0]}\\{date[1]}\\{date[2]}\\{f_object.name}"
            upload_dir = os.path.join(settings.MEDIA_ROOT, file_path)
            try:
                os.makedirs(os.path.dirname(upload_dir), exist_ok=True)

                def _run_async():
                    """
                    There is we open the new loop and uploading file.
                    Our user don't waiting for us - when we will finish the upload.
                    :return: void.
                    """
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(handle_uploaded_file(upload_dir, file))

                # OPEN NEW THREAD
                thread = threading.Thread(target=_run_async)
                thread.start()
                thread.join()
            except Exception as e:
                log.error(f"{error_text} Error => %s", e.args[0])
                return Response(
                    {"errors": f"{error_text} Error => {e.args[0]}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]


# запустить celery
# сделать refer  а парсинг
# сдулать удаление только для продусера и админа
# Сделать роутер к базе данных
