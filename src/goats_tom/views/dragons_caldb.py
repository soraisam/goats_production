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
        file_path_or_name = serializer.validated_data["file"]

        try:
            if action == "add":
                serializer.instance.add_caldb_file(file_path_or_name)

            elif action == "remove":
                serializer.instance.remove_caldb_file(file_path_or_name)

        except Exception:
            # TODO: Add erorr handling?
            pass
