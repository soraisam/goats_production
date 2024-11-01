__all__ = ["DataProductDeleteView"]
from django.http import (
    HttpResponseRedirect,
)
from tom_dataproducts.views import DataProductDeleteView as BaseDataProductDeleteView

from goats_tom.utils import delete_associated_data_products


class DataProductDeleteView(BaseDataProductDeleteView):
    def form_valid(self, form):
        """Method that handles DELETE requests for this view. It performs the
        following actions in order:
        1. Deletes all ``ReducedDatum`` objects associated with the
        ``DataProduct``.
        2. Deletes the file referenced by the ``DataProduct``.
        3. Deletes the ``DataProduct`` object from the database.

        :param form: Django form instance containing the data for the DELETE
        request.
        :type form: django.forms.Form
        :return: HttpResponseRedirect to the success URL.
        :rtype: HttpResponseRedirect
        """
        # Fetch the DataProduct object
        data_product = self.get_object()
        delete_associated_data_products(data_product)

        return HttpResponseRedirect(self.get_success_url())
