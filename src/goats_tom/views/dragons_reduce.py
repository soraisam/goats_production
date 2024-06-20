"""Module for DRAGONSReduce view set."""

__all__ = ["DRAGONSReduceViewSet"]
from dramatiq_abort import abort
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from goats_tom.models import DRAGONSReduce
from goats_tom.realtime import DRAGONSProgress, NotificationInstance
from goats_tom.serializers import (
    DRAGONSReduceFilterSerializer,
    DRAGONSReduceSerializer,
    DRAGONSReduceUpdateSerializer,
)
from goats_tom.tasks import run_dragons_reduce


class DRAGONSReduceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = DRAGONSReduce.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_serializer_class = DRAGONSReduceFilterSerializer
    serializer_classes = {
        "update": DRAGONSReduceUpdateSerializer,
        "partial_update": DRAGONSReduceUpdateSerializer,
    }
    serializer_class = DRAGONSReduceSerializer

    def get_serializer_class(self):
        """Determine which serializer to use based on the HTTP method."""
        return self.serializer_classes.get(self.action, self.serializer_class)

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
        task_id = run_dragons_reduce.send(reduce.id)
        reduce.task_id = task_id.message_id
        reduce.save()

    def perform_update(self, serializer: DRAGONSReduceUpdateSerializer) -> None:
        """Cancels a task.

        Parameters
        ----------
        serializer : `DRAGONSReduceUpdateSerializer`.
        """
        reduce = serializer.save()
        if reduce.status == "canceled":
            # Cancel the running event.
            abort(reduce.task_id)
            DRAGONSProgress.create_and_send(reduce)
            NotificationInstance.create_and_send(
                label=reduce.get_label(),
                color="warning",
                message="Background task canceled.",
            )
