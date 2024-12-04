__all__ = ["Antares2GoatsSerializer"]

from rest_framework import serializers


class Antares2GoatsSerializer(serializers.Serializer):
    esquery = serializers.JSONField(required=False, allow_null=True)
    locusid = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        """Check that either 'esquery' or 'locusid' is provided."""
        esquery = data.get("esquery", None)
        locusid = data.get("locusid", None)

        if not esquery and not locusid:
            raise serializers.ValidationError(
                "Either 'esquery' or 'locusid' must be provided."
            )
        if esquery and locusid:
            raise serializers.ValidationError(
                "Only one of 'esquery' or 'locusid' should be provided."
            )

        return data
