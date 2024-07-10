from rest_framework import serializers

from goats_tom.models import DRAGONSRecipe


class DRAGONSRecipeSerializer(serializers.ModelSerializer):
    """Serializer for `DRAGONSRecipe` models."""

    active_function_definition = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()

    class Meta:
        model = DRAGONSRecipe
        fields = (
            "id",
            "dragons_run",
            "file_type",
            "name",
            "function_definition",
            "short_name",
            "active_function_definition",
        )
        read_only_fields = (
            "id",
            "dragons_run",
            "file_type",
            "name",
            "short_name",
            "active_function_definition",
        )
        extra_kwargs = {"function_definition": {"write_only": True}}

    def get_active_function_definition(self, instance: DRAGONSRecipe) -> str:
        return instance.active_function_definition

    def get_short_name(self, instance: DRAGONSRecipe):
        return instance.short_name

    def update(self, instance: DRAGONSRecipe, validated_data: dict) -> DRAGONSRecipe:
        # Check if "function_definition" key exists in the validated data.
        if "function_definition" in validated_data:
            func_def = validated_data["function_definition"]

            # Check if "function_definition" is `None` or effectively empty.
            if func_def is None or func_def.strip() == "":
                instance.reset_to_original(save=False)
            else:
                instance.function_definition = func_def
            instance.save()
        # If the key is not present, do nothing regarding the function field.
        return instance


class DRAGONSRecipeFilterSerializer(serializers.Serializer):
    """Serializer for filtering `DRAGONS` recipes."""

    dragons_run = serializers.IntegerField(
        required=False, help_text="Primary key for the DRAGONS run to filter by."
    )
    # TODO: This should be a choice of options for file_type to validate
    file_type = serializers.CharField(
        required=False, help_text="File type to filter by."
    )
    include = serializers.ListField(
        child=serializers.ChoiceField(choices=["help"]), required=False
    )
