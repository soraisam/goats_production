__all__ = ["DRAGONSView"]

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from tom_observations.models import ObservationRecord


class DRAGONSView(LoginRequiredMixin, View):
    """A Django view for displaying the DRAGONS page."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Handles GET requests to display DRAGONS.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.
        pk : `int`
            The primary key of the `ObservationRecord`.

        Returns
        -------
        `HttpResponse`
            The rendered DRAGONS page.

        """
        observation_record = get_object_or_404(ObservationRecord, pk=pk)
        dragons_runs = observation_record.dragons_runs.all()

        # Get the available folders for display.
        return render(
            request,
            "dragons_index.html",
            {"observation_record": observation_record, "dragons_runs": dragons_runs},
        )
