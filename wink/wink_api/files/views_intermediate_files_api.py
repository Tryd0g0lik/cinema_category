from adrf import viewsets
from rest_framework import status, permissions
from wink.models_wink.files import IntermediateFilesModel
from wink.wink_api.files.serialisers import IntermediateFilesSerializer


class IntermediateFilesViewSet(viewsets.ModelViewSet):
    queryset = IntermediateFilesModel.objects.all()
    serializer_class = IntermediateFilesSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Из фрнта приходит заявка, что файл отправить на анализ.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
