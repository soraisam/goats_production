"""Module to serializer data for `DRAGONSFile` model."""

__all__ = ["DRAGONSFileSerializer", "DRAGONSFileFilterSerializer"]

from rest_framework import serializers

from goats_tom.models import DRAGONSFile


class DRAGONSFileSerializer(serializers.ModelSerializer):
    """Serializer for `DRAGONSFile` model."""

    class Meta:
        model = DRAGONSFile
        fields = [
            "id",
            "dragons_run",
            "product_id",
            "url",
            "observation_id",
            "file_type",
            "object_name",
            "enabled",
        ]
        read_only_fields = [
            "id",
            "dragons_run",
            "product_id",
            "url",
            "observation_id",
            "file_type",
            "object_name",
        ]

    def update(self, instance, validated_data):
        instance.enabled = validated_data.get("enabled", instance.enabled)
        instance.save()
        return instance


class DRAGONSFileFilterSerializer(serializers.Serializer):
    group_by_file_type = serializers.BooleanField(required=False, default=False)
    dragons_run = serializers.IntegerField(required=False)
    include = serializers.ListField(
        child=serializers.ChoiceField(choices=["header", "groups"]),
        required=False,
    )
