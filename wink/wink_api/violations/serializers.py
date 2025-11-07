from adrf import serializers

from wink.models_wink.violations import BasisViolation


class BasisViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasisViolation
        fields = "__all__"
