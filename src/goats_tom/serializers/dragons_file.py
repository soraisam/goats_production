"""Module to serializer data for `DRAGONSFile` model."""

__all__ = ["DRAGONSFileSerializer", "DRAGONSFileFilterSerializer"]

from urllib.parse import unquote

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
            "astrodata_descriptors",
        ]
        read_only_fields = [
            "id",
            "dragons_run",
            "product_id",
            "url",
            "observation_id",
            "file_type",
            "object_name",
            "astrodata_descriptors",
        ]

    def update(self, instance, validated_data):
        instance.enabled = validated_data.get("enabled", instance.enabled)
        instance.save()
        return instance


class DRAGONSFileFilterSerializer(serializers.Serializer):
    group_by_file_type = serializers.BooleanField(required=False, default=False)
    dragons_run = serializers.IntegerField(required=False)
    file_type = serializers.CharField(required=False)
    object_name = serializers.CharField(required=False, allow_blank=True)
    include = serializers.ListField(
        child=serializers.ChoiceField(choices=["header", "groups"]),
        required=False,
    )
    group_by = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="A list of groups to filter by.",
    )
    filter_expression = serializers.CharField(required=False, allow_blank=True)
    filter_strict = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Use a tolerance for filtering numeric values.",
    )

    def validate(self, data):
        """
        Custom validation to enforce logic rules for grouping and filtering.
        """
        group_by_file_type = data.get("group_by_file_type", False)
        group_by = data.get("group_by", [])
        file_type = data.get("file_type", "")
        object_name = data.get("object_name", "")
        # dragons_run = data.get("dragons_run", None)

        # When group_by_file_type is True, ensure no group_by, file_type, or
        # object_name is provided
        if group_by_file_type:
            if group_by or file_type or object_name:
                raise serializers.ValidationError(
                    "When 'group_by_file_type' is true, 'group_by', 'file_type', and "
                    "'object_name' should not be included."
                )

        # group_by is required for file_type and object_name
        # if not group_by:
        #     if file_type:
        #         raise serializers.ValidationError(
        #             "'file_type' can only be included if 'group_by' is provided."
        #         )
        #     if object_name:
        #         raise serializers.ValidationError(
        #             "'object_name' can only be included if 'group_by' is provided."
        #         )

        # # If group_by is used, ensure that dragons_run and file_type are provided
        # if group_by:
        #     if not dragons_run:
        #         raise serializers.ValidationError(
        #             "'dragons_run' is required when 'group_by' is used."
        #         )
        #     if not file_type:
        #         raise serializers.ValidationError(
        #             "'file_type' is required when 'group_by' is used."
        #         )
        #     # If file_type is 'object', object_name must also be provided
        #     if file_type == "object" and not object_name:
        #         raise serializers.ValidationError(
        #             "'object_name' is required when 'file_type' is 'object' and "
        #             "'group_by' is used."
        #         )

        return data

    def to_internal_value(self, data):
        new_data = data.copy()
        new_data["filter_expression"] = unquote(data.get("filter_expression", ""))
        return super().to_internal_value(new_data)
