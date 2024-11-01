__all__ = ["ObservationRecordDetailView"]
from django.urls import reverse
from django.views.generic import DetailView
from tom_dataproducts.forms import AddProductToGroupForm, DataProductUploadForm
from tom_observations.facility import BaseManualObservationFacility
from tom_observations.facility import (
    get_service_class as tom_observations_get_service_class,
)
from tom_observations.views import (
    ObservationRecordDetailView as BaseObservationRecordDetailView,
)


class ObservationRecordDetailView(BaseObservationRecordDetailView):
    """View to override creating thumbnails."""

    def get_context_data(self, *args, **kwargs):
        """Override for avoiding "get_preview" and creating thumbnail."""
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context["form"] = AddProductToGroupForm()
        facility = tom_observations_get_service_class(self.object.facility)()
        facility.set_user(self.request.user)
        observation_record = self.get_object()

        context["editable"] = isinstance(facility, BaseManualObservationFacility)
        context["data_products"] = facility.all_data_products(self.object)
        context["can_be_cancelled"] = (
            self.object.status not in facility.get_terminal_observing_states()
        )
        context["target"] = observation_record.target
        data_product_upload_form = DataProductUploadForm(
            initial={
                "observation_record": observation_record,
                "referrer": reverse(
                    "tom_observations:detail",
                    args=(self.get_object().id,),
                ),
            },
        )
        context["data_product_form"] = data_product_upload_form
        context["observation_id"] = observation_record.observation_id
        return context
