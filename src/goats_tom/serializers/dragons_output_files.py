"""Module to serialize DRAGONSRun output files."""

__all__ = ["DRAGONSOutputFilesSerializer"]

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

    class Meta:
        model = DRAGONSRun
        fields = ("files",)
        read_only_fields = ("files",)
