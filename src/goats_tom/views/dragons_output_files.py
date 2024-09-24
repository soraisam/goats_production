"""Module that handles the DRAGONS output files."""

__all__ = ["DRAGONSOutputFilesViewSet"]

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from tom_dataproducts.models import DataProduct

from goats_tom.models import DRAGONSRun
from goats_tom.serializers import DRAGONSOutputFilesSerializer


class DRAGONSOutputFilesViewSet(
    mixins.RetrieveModelMixin, GenericViewSet, mixins.UpdateModelMixin
):
    """A viewset for displaying the output files of a `DRAGONSRun`."""

    queryset = DRAGONSRun.objects.all()
    serializer_class = DRAGONSOutputFilesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_serializer_class = None

    def perform_update(self, serializer: DRAGONSOutputFilesSerializer) -> None:
        action = serializer.validated_data["action"]
        if action == "remove":
            filename = serializer.validated_data["filename"]
            product_id = serializer.validated_data["product_id"]

            # Delete the dataproduct if it exists if not use the remove_output_file.
            try:
                with transaction.atomic():
                    # Check if there is a dataproduct.
                    try:
                        dataproduct = DataProduct.objects.get(product_id=product_id)
                        dataproduct.delete()

                    except ObjectDoesNotExist:
                        # Use the instance to remove the file.
                        serializer.instance.remove_output_file(filename)
            except Exception:
                # TODO: Should I return something better?
                return
