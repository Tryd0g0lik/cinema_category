"""
wink/wink_api/violations/views_violations_api.py
"""

from adrf import viewsets
from rest_framework import permissions

from wink.models_wink.violations import BasisViolation
from wink.wink_api.violations.serializers import BasisViolationSerializer


class BasisViolationViewSet(viewsets.ModelViewSet):
    queryset = BasisViolation.objects.all()
    serializer_class = BasisViolationSerializer
    permission_classes = [permissions.AllowAny]
