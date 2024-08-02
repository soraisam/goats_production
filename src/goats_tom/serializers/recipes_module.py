__all__ = ["RecipesModuleSerializer"]

from rest_framework import serializers

from goats_tom.models import RecipesModule


class RecipesModuleSerializer(serializers.ModelSerializer):
    """Serializer for the `RecipesModule` model."""

    class Meta:
        model = RecipesModule
        fields = "__all__"
        read_only_fields = ("name", "version", "instrument")
