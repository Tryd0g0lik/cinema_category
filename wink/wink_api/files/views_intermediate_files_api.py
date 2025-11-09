from adrf import viewsets
import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from wink.models_wink.files import IntermediateFilesModel, FilesModel
from wink.models_wink.violations import BasisViolation
from wink.tasks.task_start_rotation import start_rotation
from wink.wink_api.files.serialisers import IntermediateFilesSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""
            Событие от пользователя - отправляет файл парсинг.
            That is get the data from request and save them.
            Then send a signal on AI for would be to begin load (parsing) the file
        """,
        tage=["cinema"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["file_id"],
            properties={
                "file_id": openapi.Schema(
                    openapi.IN_BODY,
                    description="This is the id of the one file",
                    type=openapi.TYPE_INTEGER,
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
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=7),
                        "violations_quantity": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="""
                            It doesn't use,now. That is the static number and all the time this the variable will have the number 0.
                            Basic goal is to provide the variable Where we can  insert a quantity of violations
                            """,
                            example=0,
                        ),
                        "upload": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="That is the index of file (refer key). It will be send to the parser.",
                            example=7,
                        ),
                        "user": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="That is the index of user. This user who sent the one file to the parser.",
                        ),
                        "violations": openapi.Schema(
                            description="This is array from any of violations - total list for determine violations as a static title. Swagger key is 'violations' ",
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                example=[
                                    1,
                                    2,
                                    3,
                                    4,
                                    5,
                                    6,
                                ],
                            ),
                        ),
                    },
                ),
            ),
            400: "Request is invalid.",
            404: "File with id does not exist.",
            500: "Internal Server Error.",
        },
    )
    def create(self, request, *args, **kwargs):
        """
        IA событие - API URL в котором pathname содержит id (refer-key)
        descript :  This method is used when - user return file to the analyze (to the AI parse).
        Body of method contain the simple logic:
        - request.body contain the id ("`file_id`") of the user file.
        - we got id and  create a new line to the "`IntermediateFilesModel`" of db.
        - then, we will send a signal to the AI - that is time download the file by the refer key.
        - and start of celery task - that begin is - follow by condition:
            > the total time of live  for a refer key is 90 second.
            > and avery 10 minutes the refer key will be updated.
            > and the one file can use only 10 users.
        Note: From "`FileReadOnlyModel`", AI can download.
        :param request:
        :param args:
        :param kwargs:
        :return: ```json
            {
                "id": 1,
                "violations_quantity": 0,
                "refer": "",
                "upload": 7,
                "user": 3,
                "violations": []
            }
            ```
        """
        error_text = "[%s.%s]:" % (
            __class__,
            self.create.__name__,
        )
        # ОТПРАВИТЬ СИГНАЛ НА AI ЧТОБ НАЧИНАЛА КАЧАТЬ
        user = request.user
        file_id = request.data.get("file_id")
        if file_id and file_id != "":
            try:
                file = FilesModel.objects.filter(id=file_id)
                all_violations = BasisViolation.objects.all()
                if len(file) == 0:
                    return Response(
                        {
                            "errors": f"{error_text} => File's id '{file_id}' is invalid. "
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                intermediate_file = IntermediateFilesModel.objects.create(
                    user=user, upload=file.first()
                )
                intermediate_file.violations.set(all_violations)
                serializer = self.get_serializer(intermediate_file)
                # refer = serializer.data["refer"].strip()
                # -------------- AI REQUEST --------------
                # тут отправляем GET запрос на AI + refer в URL-е
                # ----------------------------------------
                # -------------- START THE CELERY --------
                # The django's signal can use for the time then start the 'start_rotation'.
                try:
                    start_rotation.delay(serializer.data["upload"])
                except Exception as e:
                    import traceback

                    tb = traceback.format_exc()
                    log.error("[start_rotation]: ERROR => " + f"{str(e)} => {tb}")
                # ----------------------------------------

                ser = serializer.data
                data = {
                    "id": ser.get("id"),
                    "upload": ser.get("upload"),
                    "user": ser.get("user"),
                    "violations": ser.get("violations"),
                    "violations_quantity": ser.get("violations_quantity"),
                }

                return Response(data, status=status.HTTP_201_CREATED)
            except (FilesModel.DoesNotExist, BasisViolation.DoesNotExist) as error:
                return Response(
                    {
                        "errors": f"{error_text} => File with id '{file_id}' not found or {str(error)}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response(
                    {"errors": f"{error_text} => {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(
            {"errors": f"{error_text} => File ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
