import os.path

from adrf import views
import logging

from django.http import FileResponse
from django.apps import apps
from django.shortcuts import get_object_or_404
from pycparser.ply.cpp import t_error
from rest_framework import status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from logs import configure_logging
from wink.tasks.task_start_rotation import stop_rotation
from wink.wink_api.files.views_files_api import FilesViewSet

IntermediateFilesModel = apps.get_model("wink", "IntermediateFilesModel")
FilesModel = apps.get_model("wink", "FilesModel")

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class FileReadOnlyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""
        `Событие от AI` - получает файл для парсинг файла.
        HTTP Method is 'GET http://127.0.0.1:8000/api/v1/wink/download/<str:refer>/'.
        '<str:id>' it's the refer key of file.
        From `**kwargs` we get the two variables:
         - kwargs['id'] is the refer file's key - the type string;
         By this refer (only if we find the refer key in db) the our AI begin downloading the file.
         **``NOT`: How can we send a signal for user if the refer key is not found in the db !!!** This is we can see the status code 404.
        """,
        # methods=["GET"],
        tags=["ai"],
        manual_parameters=[
            openapi.Parameter(
                "refer",
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
            status.HTTP_200_OK: openapi.Response(
                description="File downloaded successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="The requested file for download and File will be  downloaded successfully",
                ),
                headers={
                    "Content-Disposition": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Attachment header with filename",
                    ),
                    "X-User-ID": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="User ID For example `headers['X-User-ID'] == 7`",
                    ),
                    "X-File-Target-Audience": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="For example `6+` or '0+",
                    ),
                },
            ),
            status.HTTP_404_NOT_FOUND: '{"errors": "[FileReadOnlyModel.retrieve]: ERROR => The refer is key did not found! Repeat the request"}',
            status.HTTP_500_INTERNAL_SERVER_ERROR: '{"errors": "ERROR => [error description]"}',
        },
    )
    def get(self, request, *args, **kwargs):
        """
        тут от меня начинают скачивать
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        error_text = "[%s.%s]:" % (__class__.__name__, self.get.__name__)
        # files's refer key
        refer = kwargs.get("refer")
        try:
            # -------------- SEARCH THE FILE BY A REFER
            intermediate_all = IntermediateFilesModel.objects.filter(refer=refer)
            if len(intermediate_all) == 0:
                t_error = f"{error_text} ERROR => The refer's key didn't found! Repeat the request"
                log.info(t_error)
                return Response(
                    {"errors": t_error},
                    status=status.HTTP_404_NOT_FOUND,
                )
            intermediate_obj = intermediate_all[0]
            user_id = intermediate_obj.user_id
            file_id = intermediate_obj.upload.id
            file_target_audience = intermediate_obj.target_audience
            file_obj = FilesModel.objects.filter(id=file_id).first()
            if (
                not file_obj
                or not file_obj.upload
                or not os.path.exists(file_obj.upload.path)
            ):
                t_error = f"{error_text} ERROR => The file invalid."
                log.info(t_error)
                return Response(
                    {"errors": t_error},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # -------------- SENDING FILE TO THE PARSER
            file_path = file_obj.upload.path
            response = FileResponse(open(file_path, "rb"))
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(file_path)}"'
            )
            response.headers["X-User-ID"] = user_id
            response.headers["X-File-Target-Audience"] = file_target_audience
            response.headers["X-Refer-Key"] = refer
            # -------------- START THE CELERY --------
            # The django's signal can use for the time then start the 'start_rotation'.
            # STOPNING KEY
            try:
                stop_rotation.delay(user_id)
            except Exception as e:
                import traceback

                tb = traceback.format_exc()
                log.error("[start_rotation]: ERROR => " + f"{str(e)} => {tb}")

        except Exception as e:
            t_error = f"ERROR => {e.args[0]}"
            log.error(t_error)
            return Response(
                {"errors": t_error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # -------------- ALL SUCCESSFUL ----------
        return response


class FileRecordOnlyView(views.APIView):

    @swagger_auto_schema(
        operation_description="""
        `Событие от AI` - AI отправляет результат анализа файла в db.
        HTTP Method is POST http://127.0.0.1:8000/api/v1/wink/raport/
        `Note:` В разработке
        """,
        method="POST",
        tags=["ai"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refer", "user_id"],
            properties={
                "user_id": openapi.Schema(
                    openapi.IN_BODY,
                    description="User ID which was got to the method 'GET' from API's request's `HEADERS['X-User-ID']`",
                    type=openapi.TYPE_INTEGER,
                ),
                "refer": openapi.Schema(
                    openapi.IN_BODY,
                    description="Refer key which was got to the method 'GET .../api/v1/wink/download/<str:refer>/' from API's URL pathname. ",
                    type=openapi.TYPE_INTEGER,
                ),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                "X-CSRFToken",
                openapi.IN_HEADER,
                description="The X-CSRFToken header. Token 'csrftoken you cant take from the cookie or to look the API's tage 'csrf'",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "в разработке"},
    )
    @api_view(
        [
            "POST",
        ]
    )
    async def post(self, request, *args, **kwargs):

        f = FilesViewSet()

        try:
            # ------------ RECORD OF FILE (FROM AI) ------------
            response = await f.create(request.data, *args, **kwargs)
            user = request.user
            file_id = response.data["file_id"]
            refer = response.headers["X-Refer-Key"]
            if not file_id or not refer:
                text_error = "Maybe, refer key not found or file (from the ai) invalid."
                log.info(f"[FileRecordOnlyModel]: ERROR => {text_error}"),
                return Response(
                    {"errors": text_error}, status=status.HTTP_404_NOT_FOUND
                )
            # ------------ UPDATE TABLE - ADDITIONAL ID --------
            f_ai_list = IntermediateFilesModel.objects.filter(refer=refer)
            if not f_ai_list.first():
                text_error = "File (from the ai) didn't was found."
                log.info(f"[FileRecordOnlyModel]: ERROR => {text_error}"),
                return Response(
                    {"errors": text_error}, status=status.HTTP_404_NOT_FOUND
                )
            f_ai = f_ai_list.first()
            f_ai.update(upload_ai=file_id)

        except Exception as e:
            text_error = e.args[0]
            log.error(f"[FileRecordOnlyModel]: ERROR => {text_error}"),
            return Response(
                {"errors": text_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # ------------ ALL SUCCESSFUL ----------------------
        return Response(status=status.HTTP_200_OK)
