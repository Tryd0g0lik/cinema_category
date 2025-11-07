import asyncio
import datetime
import logging
import threading
import os
from adrf import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from wink.wink_api.files.serialisers import FilesSerializer
from wink.models_wink.files import (
    FilesModel,
)
from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


async def handle_uploaded_file(path: str, f, index: int):
    """
    :param str path:
    :param f: it from django's 'request.FILES["upload"]'
    :param int index:
    :return: void
    """
    with open(path, "wb+") as destination:
        for chunk in f.chunks(10 * 1024 * 1024):
            destination.write(chunk)
    path = path.split("upload")[1].replace("\\", "/")
    f_oblect = await asyncio.to_thread(lambda: FilesModel.objects.get(id=index))
    f_oblect.upload = f"media/upload{path}"
    await f_oblect.asave()


class FilesViewSet(viewsets.ModelViewSet):
    queryset = FilesModel.objects.all()
    serializer_class = FilesSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""This method record meta-data about files and the 'upload' field is do empty. It's for the main flow.
            Then, It create the new thread and inside of thread it upload the file to the server by server's path 'media/upload/%Y/%m/%d/file_name.{pdf|docx}'
            Then, column 'upload' is updating from the last row's empty in the database.
            Note: Record of file to the server and send it on parsing - this is two separate processes!
            That is just the process a saving.
        """,
        tags=["files"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["upload"],
            properties={
                "upload": openapi.Schema(
                    openapi.IN_FORM,
                    description="The upload file. 'Content-Type: multipart/form-data' is request.",
                    type=openapi.TYPE_FILE,
                ),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                "X-CSRFToken",
                openapi.IN_HEADER,
                description="The X-CSRFToken header. Token 'csrftoken you cant take from the cookie or to look the API's tage 'csrf'",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="If all nice means the response contain just the status code 200. ",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12)
                    },
                ),
            ),
            400: "{'errors': 'text of error'}",
        },
    )
    async def create(self, request, *args, **kwargs):
        """
        NODE: The method don't use the check on the duplicate!!!
        """
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
                    loop.run_until_complete(
                        handle_uploaded_file(upload_dir, file, f_object.id)
                    )

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
        return Response(data={"id": f_object.id}, status=status.HTTP_201_CREATED)
