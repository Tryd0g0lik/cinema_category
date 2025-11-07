from adrf import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions
from wink.models_wink.files import IntermediateFilesModel
from wink.wink_api.files.serialisers import IntermediateFilesSerializer


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]
