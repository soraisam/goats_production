"""Module to serialize DRAGONSRun calibration database."""

__all__ = ["DRAGONSCaldbSerializer"]

from pathlib import Path
from typing import Any

from rest_framework import serializers

from goats_tom.models import DRAGONSRun


class DRAGONSCaldbSerializer(serializers.ModelSerializer):
    """Serializer for handling actions on the calibration database of DRAGONS runs.

    Attributes
    ----------
    files : `serializers.SerializerMethodField`
        A field that gets a list of files from the `DRAGONSRun` instance.
    file : `serializers.CharField`
        The file path for adding a new file or the name of the file to remove.
    action : `serializers.ChoiceField`
        Specifies the action to be performed on the calibration database.
    """

    files = serializers.SerializerMethodField()
    file = serializers.CharField(
        write_only=True,
        max_length=255,
        help_text="Path for the new file to add",
        required=True,
    )
    action = serializers.ChoiceField(
        choices=["remove", "add"],
        write_only=True,
        help_text="Actions to perform on the calibration database.",
        required=True,
    )

    def get_files(self, obj: DRAGONSRun) -> list[dict[str, str]]:
        """Retrieves a list of files from the calibration database.

        Parameters
        ----------
        obj : `DRAGONSRun`
            The instance of `DRAGONSRun` from which to retrieve files.

        Returns
        -------
        `list[dict[str, str]]`
            A list of dictionaries, each containing 'name' and 'path' of a file.
        """
        return obj.list_caldb_files()

    class Meta:
        model = DRAGONSRun
        fields = ("id", "files", "file", "action")
        read_only_fields = ("files", "id")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validates the requested action against the calibration database files.

        Parameters
        ----------
        attrs : `dict[str, Any]`
            Dictionary of attributes to be validated.

        Raises
        ------
        serializers.ValidationError
            Raised if the file does not exist for removal or already exists for adding.

        Returns
        -------
        `dict[str, Any]`
            The validated attributes.
        """
        action = attrs.get("action")
        file_path_or_name = attrs.get("file")
        files = {
            Path(file["path"]) / file["name"]
            for file in self.instance.list_caldb_files()
        }

        if action == "add":
            file_path = Path(file_path_or_name)
            if any(file_path.resolve() == fp.resolve() for fp in files):
                raise serializers.ValidationError(
                    {"file": "This file already exists in the calibration database."}
                )
            if not file_path.exists():
                raise serializers.ValidationError(
                    {"file": "The file does not exist at the provided path."}
                )

        elif action == "remove":
            file_names = {fp.name for fp in files}
            if file_path_or_name not in file_names:
                raise serializers.ValidationError(
                    {"file": "The file does not exist in the calibration database."}
                )

        return attrs
