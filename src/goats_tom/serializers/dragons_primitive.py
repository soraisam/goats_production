"""Module for serializing DRAGONS primitives and filters."""

from rest_framework import serializers

from goats_tom.models import DRAGONSPrimitive


class DRAGONSPrimitiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRAGONSPrimitive
        fields = "__all__"


class DRAGONSPrimitiveFilterSerializer(serializers.Serializer):
    recipe = serializers.IntegerField(
        required=False, help_text="Primary key for the recipe to filter by"
    )
