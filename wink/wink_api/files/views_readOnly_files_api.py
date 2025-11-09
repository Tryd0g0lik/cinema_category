import asyncio
import os.path

from adrf import views
import logging

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from logs import configure_logging
from wink.models_wink.files import IntermediateFilesModel, FilesModel
from wink.tasks.task_start_rotation import stop_rotation

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class FileReadOnlyModel(views.APIView):
    # queryset = IntermediateFilesModel.objects.all()
    # serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""
        Событие от AI - парсинг файла.
        HTTP Method is '`GET`'.
        From `**kwargs` we get the two variables:
         - kwargs['id'] is the refer file's key - the type string;
         By this refer (only if we find the refer key in db) the our AI begin downloading the file.
         **``NOT`: How can we send a signal for user if the refer key is not found in the db !!!** This is we can see the status code 404.
        """,
        tags=["download"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="""
                ID is the refer file's key - the type string. Example: 'f897f411a4944abea63d6358e89833b2'
                `NOTE:` С ключём ещё работаю. В любой момент может измениться - состав символов.
                """,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="File downloaded successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="The requested file for download and File will be  downloaded successfully",
                ),
                header={
                    "Content-Disposition": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Attachment header with filename",
                    )
                },
            ),
            404: '{"errors": "[FileReadOnlyModel.retrieve]: ERROR => The refer is key did not found! Repeat the request"}',
            500: '{"errors": "ERROR => [error description]"}',
        },
    )
    async def get(self, request, *args, **kwargs):
        # async def retrieve(self, request, *args, **kwargs):
        """
        тут от меня начинают скачивать
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        error_test = "[%s.%s]:" % (__class__.__name__, self.get.__name__)

        pk = kwargs.get("pk")
        try:
            intermediate_all = [
                view async for view in IntermediateFilesModel.objects.filter(refer=pk)
            ]

            if len(intermediate_all) == 0:
                return Response(
                    {
                        "errors": f"{error_test} ERROR => The refer's key didn't found! Repeat the request"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            intermediate_obj = intermediate_all[0]
            user_id = await asyncio.to_thread(lambda: intermediate_obj.user_id)
            file_id = await asyncio.to_thread(lambda: intermediate_obj.upload.id)
            file_obj = await asyncio.to_thread(
                lambda: get_object_or_404(FilesModel, id=file_id)
            )
            if not file_obj.upload or not os.path.exists(file_obj.upload.path):
                return Response(
                    {"errors": f"{error_test} ERROR => The file invalid."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            file_path = file_obj.upload.path
            response = await asyncio.to_thread(
                lambda: FileResponse(open(file_obj.upload.path, "rb"))
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(file_path)}"'
            )
            # -------------- START THE CELERY --------
            # The django's signal can use for the time then start the 'start_rotation'.
            try:
                await stop_rotation.delay(user_id)
            except Exception as e:
                import traceback

                tb = traceback.format_exc()
                log.error("[start_rotation]: ERROR => " + f"{str(e)} => {tb}")

            return response
        except Exception as e:
            return Response(
                {"errors": f"ERROR => {e.args[0]}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
