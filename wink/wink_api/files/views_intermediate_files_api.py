import asyncio
from adrf import viewsets
import logging
from rest_framework import status, permissions
from rest_framework.response import Response

from wink.models_wink.files import IntermediateFilesModel, FilesModel
from wink.models_wink.violations import BasisViolation
from wink.signals import user_comment_signal, file_upload_signal

from wink.wink_api.files.serialisers import IntermediateFilesSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from logs import configure_logging
from wink.wink_api.files.views_files_api import FilesViewSet

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""
            `Событие от` пользователя - данные из формы - файл парсинг, целефая аудитория.
            That is get the data from request and save them.
            Then send a signal on AI for would be to begin load (parsing) the file

        """,
        tage=["cinema"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["upload", "target_audience"],
            properties={
                "upload": openapi.Schema(
                    openapi.IN_FORM,
                    description="The upload file. 'Content-Type: multipart/form-data' is request.",
                    type=openapi.TYPE_FILE,
                ),
                "target_audience": openapi.Schema(
                    openapi.IN_FORM,
                    description="The 'target_audience' - target audience - Exemple: 0+ or 6+ ",
                    type=openapi.TYPE_STRING,
                ),
                "comment": openapi.Schema(
                    openapi.IN_FORM,
                    description="Comment. Simply, you can insert the empty low/string. Exemple: '"
                    "' or null  ",
                    type=openapi.TYPE_STRING,
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
                            description="That is the index from 'IntermediateFilesModel'. This is the file which be send to the parser.",
                            example=7,
                        ),
                        "upload_ai": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="That is the index from 'IntermediateFilesModel'. This is the file  which was got from the parser.  The default value is null/None",
                            example=7,
                        ),
                        "status_file": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Status has four of values. 1) '--------' is by default, 2) 'processing' is when the file is sent for processing, 3) 'ready' is all successful and completed. 4) 'error'.",
                            example="--------",
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
    async def create(self, request, *args, **kwargs):
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
        Note: ОЗДАТЬ ПРОВЕРКУ НА ДУБЛИКАТ ФАЙЛОВ иначе подится куаук/ На данный
            момент, зпереименовать или ждать один день. После повторить загрузку.

        In the body of method we can see the 'requests.get'. From here - we have sending the
         request by the GET method (to the AI side) and insert the refer-key of file (for pars).
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
        url_ai = "/api/v1/wink/get/889e986a9512455984edee82c53d7301/"
        error_text = "[%s.%s]:" % (
            __class__,
            self.create.__name__,
        )

        user = request.user
        file_id = None

        try:
            # -------------- GET THE ID OF NEW FILE --------
            if request.FILES["upload"]:

                f = FilesViewSet()
                res = await f.create(request, *args, **kwargs)
                file_id = res.data["id_file"]
            else:
                t_error = f"{error_text} Error => 'request.FILES['upload']' is invalid!"
                log.info(t_error)
                return Response({"errors": t_error}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            t_error = f"{error_text} Error => {e.args[0]}"
            log.info(t_error)
            return Response({"errors": t_error}, status=status.HTTP_400_BAD_REQUEST)
        # ----------------------------------------------
        target_audience = request.data.get("target_audience")
        comment = request.data.get("comment")
        index = None
        if file_id and isinstance(file_id, int):
            try:

                file = await asyncio.to_thread(
                    lambda: FilesModel.objects.get(id=file_id)
                )
                # ---- СОЗДАТЬ ПРОВЕРКУ НА ДУБЛИКАТ ФАЙЛОВ
                if not file:
                    return Response(
                        {
                            "errors": f"{error_text} => File's id '{file_id}' is invalid. "
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                intermediate_file = await IntermediateFilesModel.objects.acreate(
                    user=user,
                    upload=file,
                    target_audience=target_audience,
                    status_file="processing",
                )
                index = intermediate_file.id
                serializer = self.get_serializer(intermediate_file)
                try:

                    if comment is not None and len(comment) > 0:
                        # -------------- SIGNAL - RECORDING THE USER's COMMENT
                        #  Here, we work with user comments - they, was sent to the AI parser process.

                        kwargs = {
                            "user_id": user.id,
                            "comment": comment,
                            "file_id": file_id,
                            "author": "User",
                        }
                        user_comment_signal.send(sender=self.__class__, **kwargs)
                        log.info("Signal START & Sender: %s", (self.create.__name__,))

                    # -------------- SIGNAL - AI FOR UPLOAD A FILE BY REFER

                    kwargs = {"refer": intermediate_file.refer.hex}
                    file_upload_signal.send(sender=self.__class__, **kwargs)
                except Exception as e:
                    return Response(
                        {"errors": f"{error_text} SIGNAL FOR AI: => {e.args[0]}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # -------------- START THE CELERY --------
                # The django's signal can use for the time then start the 'start_rotation'.
                try:
                    from wink.tasks.task_start_rotation import start_rotation

                    await asyncio.to_thread(
                        lambda: start_rotation.delay(serializer.data["upload"])
                    )
                    log.info("Celery START & File ID: %s", (serializer.data["upload"],))
                except Exception as e:
                    import traceback

                    intermediate_file.status_file = "error"
                    tb = await asyncio.to_thread(lambda: traceback.format_exc())
                    log.error("[start_rotation]: ERROR => " + f"{str(e)} => {tb}")
                # ----------------------------------------

                ser = await asyncio.to_thread(lambda: serializer.data)
                data = {
                    "id": ser.get("id"),
                    "upload": ser.get("upload"),
                    "user": ser.get("user"),
                    "violations": ser.get("violations"),
                    "violations_quantity": ser.get("violations_quantity"),
                    "upload_ai": ser.get("upload_ai"),
                    "status_file": ser.get("status_file"),
                }

                return Response(data, status=status.HTTP_201_CREATED)
            except (FilesModel.DoesNotExist, BasisViolation.DoesNotExist) as error:
                intr = IntermediateFilesModel.objects.filter(id=index)
                if intr.exists():
                    intr[0].status_file = "error"
                return Response(
                    {
                        "errors": f"{error_text} => File with id '{file_id}' not found or {str(error)}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                if index:
                    intr = IntermediateFilesModel.objects.filter(id=index)
                    if intr.exists():
                        intr[0].status_file = "error"
                return Response(
                    {"errors": f"{error_text} => {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(
            {"errors": f"{error_text} => File ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
