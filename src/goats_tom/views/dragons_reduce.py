"""Module for DRAGONSReduce view set."""

__all__ = ["DRAGONSReduceViewSet"]
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from goats_tom.models import DRAGONSReduce
from goats_tom.serializers import DRAGONSReduceFilterSerializer, DRAGONSReduceSerializer
from goats_tom.tasks import run_dragons_reduce
from goats_tom.realtime import DRAGONSProgress

class DRAGONSReduceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = DRAGONSReduce.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DRAGONSReduceSerializer
    filter_serializer_class = DRAGONSReduceFilterSerializer

    def perform_create(self, serializer: DRAGONSReduceSerializer) -> None:
        """Starts the dragons reduce background task for the specified recipe.

        Parameters
        ----------
        serializer : `DRAGONSReduceSerializer`
            The serializer with data loaded.
        """
        reduce = serializer.save()
        reduce.mark_queued()
        DRAGONSProgress.create_and_send(reduce)
        run_dragons_reduce.send(reduce.id)
