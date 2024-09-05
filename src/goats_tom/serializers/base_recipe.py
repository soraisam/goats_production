__all__ = ["BaseRecipeSerializer"]

from rest_framework import serializers

from goats_tom.models import BaseRecipe


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Serializer for the `BaseRecipe` model."""

    class Meta:
        model = BaseRecipe
        fields = "__all__"
        read_only_fields = (
            "name",
            "function_definition",
            "recipes_module",
        )
