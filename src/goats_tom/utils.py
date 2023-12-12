__all__ = ["delete_associated_data_products", "create_name_reduction_map", "custom_data_product_path"]
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


def custom_data_product_path(data_product: DataProduct, filename: str) -> str:
    """Override where data products are saved. This is set in "settings.py"

    Parameters
    ----------
    data_product : `DataProduct`
        The data product to save.
    filename : `str`
        The filename to use.

    Returns
    -------
    `str`
        The path to the data product.
    """
    if data_product.observation_record is not None:
        return (f"{data_product.target.name}/{data_product.observation_record.facility}"
                f"/{data_product.observation_record.observation_id}/{filename}")
    else:
        return f"{data_product.target.name}/none/none/{filename}"
