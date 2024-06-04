"""Module for `DRAGONSReduce` serializers."""

__all__ = ["DRAGONSReduceFilterSerializer", "DRAGONSReduceSerializer"]
from rest_framework import serializers

from goats_tom.models import DRAGONSRecipe, DRAGONSReduce


class DRAGONSReduceSerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving DRAGONSReduce instances.

    Attributes
    ----------
    recipe_id : `serializers.IntegerField`
        ID of the DRAGONSRecipe instance that the reduction is associated with.
    """

    recipe_id = serializers.IntegerField(write_only=True, required=True)

    def validate_recipe_id(self, value: int) -> int:
        """Validates that the provided recipe ID corresponds to an existing
        `DRAGONSRecipe` instance.

        Parameters
        ----------
        value : `int`
            The recipe ID to be validated.

        Returns
        -------
        `int`
            The validated recipe ID.

        Raises
        ------
        `ValidationError`
            Raised if no DRAGONSRecipe exists with the provided ID.
        """
        if not DRAGONSRecipe.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipe ID does not exist")
        return value

    def create(self, validated_data: dict) -> DRAGONSReduce:
        """Creates a new `DRAGONSReduce` instance using the validated data.

        Parameters
        ----------
        validated_data : `dict`
            A dictionary containing all the validated fields.

        Returns
        -------
        `DRAGONSReduce`
            The newly created `DRAGONSReduce` instance.
        """
        recipe_id = validated_data.pop("recipe_id")
        recipe = DRAGONSRecipe.objects.get(id=recipe_id)
        # Rest of the fields are handled automatically.
        return DRAGONSReduce.objects.create(recipe=recipe)

    class Meta:
        model = DRAGONSReduce
        fields = ["id", "recipe", "recipe_id", "start_time", "end_time", "status"]
        read_only_fields = ["id", "recipe", "start_time", "end_time", "status"]


class DRAGONSReduceFilterSerializer(serializers.Serializer):
    pass
