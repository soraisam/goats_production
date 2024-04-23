"""Serializer for DRAGONSRun."""

__all__ = ["DRAGONSRunSerializer"]

from rest_framework import serializers

from goats_tom.models import DRAGONSRun


class DRAGONSRunSerializer(serializers.ModelSerializer):
    """Serializer for DRAGONSRun model instances.

    Attributes
    ----------
    observation_id : `serializers.SerializerMethodField`
        A field to include the "observation_id" from the related
        `ObservationRecord` model instance.
    """

    observation_id = serializers.SerializerMethodField()

    class Meta:
        """Meta class for configuration."""

        model = DRAGONSRun
        fields = "__all__"

    def get_observation_id(self, obj: DRAGONSRun) -> str:
        """
        Returns the "observation_id" for the given DRAGONSRun instance.

        Parameters
        ----------
        obj : `DRAGONSRun`
            The DRAGONSRun instance being serialized.

        Returns
        -------
        `str`
            The "observation_id" of the related `ObservationRecord`.
        """
        return obj.observation_record.observation_id


class DRAGONSRunFilterSerializer(serializers.Serializer):
    observation_record = serializers.IntegerField(
        required=False, help_text="Primary key for the observation record to filter by"
    )
