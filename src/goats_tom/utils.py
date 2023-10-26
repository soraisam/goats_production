from tom_dataproducts.models import DataProduct, ReducedDatum
from tom_observations.models import ObservationRecord


def delete_associated_data_products(observation_record: ObservationRecord) -> None:
    """Utility function to delete associated DataProducts.

    Parameters
    ----------
    observation_record : `ObservationRecord`
        The ObservationRecord object to find associated DataProducts.
    """
    query = DataProduct.objects.filter(observation_record=observation_record)
    for data_product in query:
        # Delete associated ReducedDatum objects.
        ReducedDatum.objects.filter(data_product=data_product).delete()

        # Delete the file from the disk.
        data_product.data.delete()

        # Delete thumbnail from the disk.
        data_product.thumbnail.delete()

        # Delete the `DataProduct` object from the database.
        data_product.delete()
