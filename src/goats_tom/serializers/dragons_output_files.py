"""Module to serialize DRAGONSRun output files."""

__all__ = ["DRAGONSOutputFilesSerializer"]

from django.core.files.storage import default_storage
from rest_framework import serializers

from goats_tom.models import DRAGONSRun


class DRAGONSOutputFilesSerializer(serializers.ModelSerializer):
    """Serializer for the output files from a DRAGONS run.

    Attributes
    ----------
    files : `serializers.SerializerMethodField`
        A field that gets a list of output files from the `DRAGONSRun` instance.
    """

    files = serializers.SerializerMethodField()
    filename = serializers.CharField(
        write_only=True,
        max_length=255,
        help_text="Filename of the file to remove.",
        required=True,
    )
    action = serializers.ChoiceField(
        choices=["remove"],
        write_only=True,
        help_text="Actions to perform to the output files.",
        required=True,
    )
    product_id = serializers.CharField(
        write_only=True, max_length=255, help_text="Product ID of the file.",
        required=True,
    )

    def get_files(self, obj: DRAGONSRun) -> list[dict[str, str]]:
        """Retrieves a list of files from the output directory.

        Parameters
        ----------
        obj : `DRAGONSRun`
            The instance of `DRAGONSRun` from which to retrieve files.

        Returns
        -------
        `list[dict[str, str]]`
            A list of dictionaries of information about a file.
        """
        return obj.get_output_files()

    def validate_filename(self, value: str) -> str:
        filepath = self.instance.get_output_dir() / value
        if not default_storage.exists(filepath):
            raise serializers.ValidationError(
                "The file does not exist at the specified path."
            )
        return value

    class Meta:
        model = DRAGONSRun
        fields = (
            "files",
            "action",
            "filename",
            "product_id",
        )
        read_only_fields = ("files",)
