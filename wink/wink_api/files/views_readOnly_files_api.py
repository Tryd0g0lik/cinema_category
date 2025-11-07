from adrf import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.request import Request

from wink.models_wink.files import IntermediateFilesModel
from wink.wink_api.files.serialisers import IntermediateFilesSerializer


class FileReadOnlyModel(viewsets.ReadOnlyModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        pass
