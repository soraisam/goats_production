"""Module for `DRAGONSReduce` serializers."""

__all__ = [
    "DRAGONSReduceFilterSerializer",
    "DRAGONSReduceSerializer",
    "DRAGONSReduceUpdateSerializer",
]
from rest_framework import serializers

from goats_tom.models import DRAGONSRecipe, DRAGONSReduce


class DRAGONSReduceUpdateSerializer(serializers.ModelSerializer):
    """Serializer to handle updating `DRAGONSReduce`."""

    class Meta:
        model = DRAGONSReduce
        fields = "__all__"

    def validate_status(self, value) -> str:
        """Ensure that the status change is valid.

        Parameters
        ----------
        value : `str`
            The value of the status change, for now only 'canceled'.

        Raises
        ------
        `ValidationError`
            Raised if status is not 'canceled'.
        `ValidationError`
            Raised if status is already a terminal state.
        """
        if value != "canceled":
            raise serializers.ValidationError(
                "Status can only be updated to 'canceled'."
            )
        if self.instance and self.instance.status in ["done", "canceled", "error"]:
            raise serializers.ValidationError(
                "Cannot change status from a terminal state."
            )
        return value

    def update(self, instance: DRAGONSReduce, validated_data: dict):
        """Update the status of a DRAGONSReduce instance and send a cancellation
        notification.

        Parameters
        ----------
        instance : `DRAGONSReduce`
            The instance of `DRAGONSReduce` being updated.
        validated_data : `dict`
            A dictionary containing validated data from the request.

        Returns
        -------
        instance : `DRAGONSReduce`
            The updated `DRAGONSReduce` instance, with the status potentially set to
            'canceled'.
        """
        status = validated_data.get("status")

        # Only need to worry about the 'canceled' status for now.
        if status is not None and status == "canceled":
            instance.mark_canceled()
        return instance


class DRAGONSReduceSerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving DRAGONSReduce instances.

    Attributes
    ----------
    recipe_id : `serializers.IntegerField`
        ID of the DRAGONSRecipe instance that the reduction is associated with.
    """

    recipe_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = DRAGONSReduce
        fields = "__all__"
        read_only_fields = ["status"]

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


class DRAGONSReduceFilterSerializer(serializers.Serializer):
    pass
