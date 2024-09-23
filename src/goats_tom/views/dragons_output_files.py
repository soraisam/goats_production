"""Module that handles the DRAGONS output files."""

__all__ = ["DRAGONSOutputFilesViewSet"]

from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from goats_tom.models import DRAGONSRun
from goats_tom.serializers import DRAGONSOutputFilesSerializer


class DRAGONSOutputFilesViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """A viewset for displaying the output files of a `DRAGONSRun`."""

    queryset = DRAGONSRun.objects.all()
    serializer_class = DRAGONSOutputFilesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_serializer_class = None
