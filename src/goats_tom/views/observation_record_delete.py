__all__ = ["ObservationRecordDeleteView"]
from django.forms import Form
from django.http import (
    HttpResponse,
)
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from tom_common.mixins import Raise403PermissionRequiredMixin
from tom_observations.models import ObservationRecord

from goats_tom.utils import delete_associated_data_products


class ObservationRecordDeleteView(Raise403PermissionRequiredMixin, DeleteView):
    """View for deleting an observation."""

    permission_required = "tom_observations.delete_observationrecord"
    success_url = reverse_lazy("observations:list")
    model = ObservationRecord

    def form_valid(self, form: Form) -> HttpResponse:
        """Handle deletion of associated DataProducts upon valid form
        submission.

        Parameters
        ----------
        form : `Form`
            The form object.

        Returns
        -------
        `HttpResponse`
            HTTP response indicating the outcome of the deletion process.

        """
        # Fetch the ObservationRecord object.
        observation_record = self.get_object()
        delete_associated_data_products(observation_record)

        return super().form_valid(form)
