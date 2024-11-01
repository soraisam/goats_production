__all__ = ["TargetDeleteView"]
from django.forms import Form
from django.http import (
    HttpResponse,
)
from tom_observations.models import ObservationRecord
from tom_targets.views import TargetDeleteView as BaseTargetDeleteView

from goats_tom.utils import delete_associated_data_products


class TargetDeleteView(BaseTargetDeleteView):
    def form_valid(self, form: Form) -> HttpResponse:
        """Handle deletion of associated observation records upon valid form
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
        target = self.get_object()
        # Fetch the ObservationRecord object.
        observation_records = ObservationRecord.objects.filter(target=target)
        for observation_record in observation_records:
            # Delete the observation data products.
            delete_associated_data_products(observation_record)
            # Delete the observation record itself.
            observation_record.delete()

        # Proceed with deletion of the object.
        return super().form_valid(form)
