from rest_framework import serializers

from goats_tom.models import DRAGONSRecipe


class DRAGONSRecipeSerializer(serializers.ModelSerializer):
    """Serializer for `DRAGONSRecipe` models."""

    short_name = serializers.SerializerMethodField()

    class Meta:
        model = DRAGONSRecipe
        fields = "__all__"

    def get_short_name(self, obj):
        return obj.short_name


class DRAGONSRecipeFilterSerializer(serializers.Serializer):
    """Serializer for filtering `DRAGONS` recipes based on `DRAGONS` run ID and file
    type.
    """

    dragons_run = serializers.IntegerField(
        required=False, help_text="Primary key for the DRAGONS run to filter by"
    )
    # TODO: This should be a choice of options for file_type to validate
    file_type = serializers.CharField(
        required=False, help_text="File type to filter by."
    )
