"""Module that handles the DRAGONS caldb API."""

__all__ = ["DRAGONSCaldbViewSet"]

from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from goats_tom.models import DRAGONSRun
from goats_tom.serializers import DRAGONSCaldbSerializer


class DRAGONSCaldbViewSet(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """A viewset for updating the `DRAGONSRun` calibration database."""

    queryset = DRAGONSRun.objects.all()
    serializer_class = DRAGONSCaldbSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_serializer_class = None

    def perform_update(self, serializer: DRAGONSCaldbSerializer) -> None:
        """Perform an action on the calibration database based on the serializer's
        validated data.

        Parameters
        ----------
        serializer : `DRAGONSCaldbSerializer`
            The serializer containing validated data for the update.
        """
        action = serializer.validated_data["action"]

        if action == "add":
            file_obj = serializer.validated_data["file"]
            cal_dir = serializer.instance.get_calibrations_uploaded_dir()
            filepath = cal_dir / file_obj.name

            try:
                # Write the uploaded file to the calibrations uploaded directory.
                with open(filepath, "wb+") as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
            except (IOError, PermissionError):
                return

            try:
                # Update the database with the new file.
                serializer.instance.add_caldb_file(filepath)
            except Exception:
                pass
            # DRAGONS does not raise an error if it's not valid for use, so need to
            # check if in database and remove if not.
            serializer.instance.clean_caldb_uploaded_files()

        elif action == "remove":
            filename = serializer.validated_data["filename"]
            try:
                # Remove the file from the database.
                serializer.instance.remove_caldb_file(filename)
            except Exception:
                return
