import base64
import json
import os.path
from io import BytesIO

from adrf import views
import logging

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse
from django.apps import apps
from rest_framework import status, permissions
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from logs import configure_logging
from wink.tasks.task_start_rotation import stop_rotation
from wink.wink_api.files.serialisers import FilesSerializer

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
        index = None
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
            index = intermediate_obj.id
            if (
                not file_obj
                or not file_obj.upload
                or not os.path.exists(file_obj.upload.path)
            ):
                intermediate_obj.status_file = "error"
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
                intermediate_obj.status_file = "error"
                import traceback

                tb = traceback.format_exc()
                log.error("[start_rotation]: ERROR => " + f"{str(e)} => {tb}")
            file_obj.status_file = "ready"
        except Exception as e:
            if index:
                intr = IntermediateFilesModel.objects.filter(id=index)
                if intr.exists():
                    intr[0].status_file = "error"
            t_error = f"ERROR => {e.args[0]}"
            log.error(t_error)
            return Response(
                {"errors": t_error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # -------------- ALL SUCCESSFUL ----------
        return response


class FileRecordOnlyView(views.APIView):

    def post(self, request, *args, **kwargs):
        """
        `Событие от AI` - получаем файл - результат парсинга.
        Сохраняем файл предоставленный AI
        :DO Проверить  как поступят данные:
         1) используется VIEW который получает файл сценария от пользователя. От пользователя поступает файл в виде данных из фармы.
         2) От AI поступает (ответ - результат анализа/парсинга) файл JSON но сохраняется через Serializer.
        """
        serializer = FilesSerializer(data=request.data)
        index = None
        try:
            # ------------ RECORD OF FILE (FROM AI) ------------
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            # ------------ GET DATA  FOR UPDATE IntermediateFilesModel
            file_id = serializer.data["id"]
            refer = request.headers["X-Refer-Key"]
            if not file_id or not refer:
                text_error = "Maybe, refer key not found or file (from the ai) invalid."
                log.info(f"[FileRecordOnlyModel]: ERROR => {text_error}"),
                return Response(
                    {"errors": text_error}, status=status.HTTP_404_NOT_FOUND
                )
            # ------------ UPDATE TABLE's LINE - ADDITIONAL ID -
            f_ai_list = IntermediateFilesModel.objects.filter(refer=refer)
            # check data
            if not f_ai_list.exists():
                text_error = "File (from the ai) didn't was found."
                log.info(f"[FileRecordOnlyModel]: ERROR => {text_error}"),
                return Response(
                    {"errors": text_error}, status=status.HTTP_404_NOT_FOUND
                )
            # save data
            f_obj = FilesModel.objects.filter(id=file_id)
            f_ai = f_ai_list.first()
            index = f_ai.id
            f_ai.upload_ai = f_obj.first()
            f_ai.status_file = "ready"
            f_ai.save()

        except Exception as e:
            if index:
                intr = IntermediateFilesModel.objects.filter(id=index)
                if intr.exists():
                    intr[0].status_file = "error"
            text_error = e.args[0]
            log.error(f"[FileRecordOnlyModel]: ERROR => {text_error}"),
            return Response(
                {"errors": text_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # ------------ ALL SUCCESSFUL ----------------------
        return Response(status=status.HTTP_200_OK)


def json_to_file(request):
    # Парсим JSON из request.body
    data = json.loads(request.body)

    # Предполагаем, что файл в base64
    file_data = base64.b64decode(data["file_data"])
    file_name = data["file_name"]
    content_type = data.get("content_type", "application/octet-stream")

    # Создаем InMemoryUploadedFile
    file_stream = BytesIO(file_data)
    file = InMemoryUploadedFile(
        file=file_stream,
        field_name="file",
        name=file_name,
        content_type=content_type,
        size=len(file_data),
        charset=None,
    )

    return file
