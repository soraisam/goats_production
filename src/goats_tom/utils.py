__all__ = ["delete_associated_data_products", "create_name_reduction_map"]
from astropy.table import Table

from tom_dataproducts.models import DataProduct, ReducedDatum
from tom_observations.models import ObservationRecord


def delete_associated_data_products(record_or_product: ObservationRecord | DataProduct) -> None:
    """Utility function to delete associated DataProducts or a single
    DataProduct.

    Parameters
    ----------
    record_or_product : ObservationRecord | DataProduct
        The ObservationRecord object to find associated DataProducts,
        or a single DataProduct to be deleted.
    """
    if isinstance(record_or_product, ObservationRecord):
        query = DataProduct.objects.filter(observation_record=record_or_product)
    elif isinstance(record_or_product, DataProduct):
        query = [record_or_product]
    else:
        raise ValueError("Invalid argument type. Must be ObservationRecord or DataProduct.")

    for data_product in query:
        # Delete associated ReducedDatum objects.
        ReducedDatum.objects.filter(data_product=data_product).delete()

        # Delete the file from the disk.
        data_product.data.delete()

        # Delete thumbnail from the disk.
        data_product.thumbnail.delete()

        # Delete the `DataProduct` object from the database.
        data_product.delete()


def create_name_reduction_map(file_list: Table) -> dict[str, str]:
    """Create a mapping from file "name" to "reduction" values from GOA.

    Parameters
    ----------
    file_list : `Table`
        Astropy `Table` containing file information.

    Returns
    -------
    `dict[str, str]`
        A dictionary mapping file 'name' to their 'reduction' values.
    """
    return {row['name']: row['reduction'] for row in file_list}
