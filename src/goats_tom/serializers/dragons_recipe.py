from rest_framework import serializers

from goats_tom.models import DRAGONSRecipe

from .dragons_primitive import DRAGONSPrimitiveSerializer


class DRAGONSRecipeSerializer(serializers.ModelSerializer):
    """Serializer for `DRAGONSRecipe` models."""

    primitives = DRAGONSPrimitiveSerializer(many=True, read_only=True)

    class Meta:
        model = DRAGONSRecipe
        fields = "__all__"


class DRAGONSRecipeFilterSerializer(serializers.Serializer):
    """Serializer for filtering `DRAGONS` recipes based on `DRAGONS` run ID and file
    type.
    """

    dragons_run = serializers.IntegerField(
        required=False, help_text="Primary key for the DRAGONS run to filter by"
    )
    file_type = serializers.CharField(
        required=False, help_text="File type to filter by."
    )
