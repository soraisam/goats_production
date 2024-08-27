"""Serializer for DRAGONSRun."""

__all__ = ["DRAGONSRunSerializer"]

import re

from rest_framework import serializers

from goats_tom.models import DRAGONSRun


class DRAGONSRunSerializer(serializers.ModelSerializer):
    """Serializer for DRAGONSRun model instances.

    Attributes
    ----------
    observation_id : `serializers.SerializerMethodField`
        A field to include the "observation_id" from the related
        `ObservationRecord` model instance.

    directory: `serializers.SerializerMethodField`
        A field to include the full path to the output directory.

    """

    observation_id = serializers.SerializerMethodField()
    directory = serializers.SerializerMethodField()

    class Meta:
        """Meta class for configuration."""

        model = DRAGONSRun
        fields = "__all__"

    def get_directory(self, obj: DRAGONSRun) -> str:
        """Returns the full path to the output directory.

        Parameters
        ----------
        obj : `DRAGONSRun`
            The `DRAGONSRun` instance being serialized.

        Returns
        -------
        `str`
            The full path to the output directory.
        """
        return f"{obj.get_output_dir()}"

    def get_observation_id(self, obj: DRAGONSRun) -> str:
        """Returns the "observation_id" for the given DRAGONSRun instance.

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

    def validate_run_id(self, value: str) -> str:
        """Validate and format the 'run_id' to ensure it is suitable for use as a
        directory name.

        Parameters
        ----------
        value : `str`
            The 'run_id' to be validated.

        Returns
        -------
        `str`
            The formatted 'run_id' with spaces replaced by underscores.
        """
        # Replace spaces with underscores and remove problematic characters.
        sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "", value.replace(" ", "_"))
        return sanitized.lower()


class DRAGONSRunFilterSerializer(serializers.Serializer):
    observation_record = serializers.IntegerField(
        required=False,
        help_text="Primary key for the observation record to filter by",
    )
    include = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                "groups",
            ]
        ),
        required=False,
    )
