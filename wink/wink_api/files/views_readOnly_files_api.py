import os.path

from adrf import viewsets
import logging

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from logs import configure_logging
from wink.models_wink.files import IntermediateFilesModel, FilesModel
from wink.wink_api.files.serialisers import IntermediateFilesSerializer


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class FileReadOnlyModel(viewsets.ReadOnlyModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""
        HTTP Method is 'GET'.
        From `**kwargs` we get the two variables:
         - kwargs['id'] is the refer file's key - the type string;
         By this refer (only if we find the refer key in db) the our AI begin downloading the file.
         **NOTE: How can we send a signal for user if the refer key is not found in the db !!!** This is we can see the status code 404.
        """,
        tage=["download"],
        monual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="ID is the refer file's key - the type string. Example: 'f897f411a4944abea63d6358e89833b2'",
                type=openapi.TYPE_STRING,
                requests=True,
            ),
        ],
        responses={
            # 200: openapi.Response(),
            404: "ERROR => The refer's key didn't found! Repeat the request.",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        тут от меня начинают скачивать
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        error_test = "[%s.%s]:" % (__class__.__name__, self.retrieve.__name__)

        pk = kwargs.get("pk")
        try:
            all_intermediate = IntermediateFilesModel.objects.filter(refer=pk)
            if all_intermediate.first() is None:
                return Response(
                    {
                        "errors": f"{error_test} ERROR => The refer's key didn't found! Repeat the request"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            intermediate_obj = all_intermediate.first()
            file_id = intermediate_obj.upload.id
            file_obj = get_object_or_404(FilesModel, id=file_id)
            if not file_obj.upload or not os.path.exists(file_obj.upload.path):
                return Response(
                    {"errors": f"{error_test} ERROR => The file invalid."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # file = file_obj.file.read()
            # file_name = os.path.basename(file_obj.file.name)
            #
            file_path = file_obj.upload.path
            response = FileResponse(open(file_obj.upload.path, "rb"))
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(file_path)}"'
            )
            return response
        except Exception as e:
            return Response(
                {"errors": f"ERROR => {e.args[0]}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
