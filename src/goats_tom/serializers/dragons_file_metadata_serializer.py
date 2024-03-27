"""Serializer for DRAGONSFileMetadata."""

__all__ = ["DRAGONSFileMetadataSerializer"]

from goats_tom.models import DRAGONSFileMetadata
from rest_framework import serializers


class DRAGONSFileMetadataSerializer(serializers.ModelSerializer):
    """Serializer for DRAGONSFileMetadata model instances, capable of fully
    serializing the instance for reading and handling partial updates.
    """

    run_id = serializers.SerializerMethodField()
    observation_id = serializers.SerializerMethodField()

    class Meta:
        model = DRAGONSFileMetadata
        fields = "__all__"
        read_only_fields = ["run_id", "observation_id"]

    def get_observation_id(self, obj):
        """Returns the observation_id from the related DRAGONSRun instance."""
        return obj.dragons_run.observation_record.observation_id

    def get_run_id(self, obj):
        """Returns the run_id from the related DRAGONSRun instance."""
        return obj.dragons_run.run_id
