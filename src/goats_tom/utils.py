"""Utility functions."""
from astropy.table import Table
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from tom_dataproducts.models import DataProduct, ReducedDatum
from tom_observations.models import ObservationRecord

from .gemini_id import GeminiID
from .models import ProgramKey, UserKey


def delete_associated_data_products(
    record_or_product: ObservationRecord | DataProduct,
) -> None:
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
        raise ValueError(
            "Invalid argument type. Must be ObservationRecord or DataProduct."
        )

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
    return {row["name"]: row["reduction"] for row in file_list}


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
        return (
            f"{data_product.target.name}/{data_product.observation_record.facility}"
            f"/{data_product.observation_record.observation_id}/{filename}"
        )
    else:
        return f"{data_product.target.name}/none/none/{filename}"


def build_json_response(
    error_message: str | None = None, error_status: int | None = status.HTTP_200_OK
) -> JsonResponse:
    """Build a JSON response.

    Parameters
    ----------
    error_message : `str`, optional
        The error message to include in the response. If `None`, the response
        indicates a successful operation.
    error_status : `int`, optional
        The HTTP status code for the response. Defaults to 200 (HTTP_200_OK).

    Returns
    -------
    `JsonResponse`
        A JSON response with either a success or error status.
    """
    if error_message:
        return JsonResponse(
            {"status": "error", "message": error_message}, status=error_status
        )

    return JsonResponse({"status": "success", "message": ""}, status=error_status)


def get_key(user: User, identifier: str) -> UserKey | ProgramKey | None:
    """Gets the key if exists for a user and either a site or a
    program/observation ID.

    Parameters
    ----------
    user : `User`
        The user the key belongs to.
    identifier : `str`
        The site (GN/GS) or the program/observation ID.

    Returns
    -------
    `UserKey | ProgramKey | None`
        The first found key (ProgramKey or UserKey), or `None` if not found.
    """
    # Check if identifier is a site.
    if identifier in GeminiID.sites:
        # Retrieve an active UserKey for the site.
        user_key = UserKey.objects.filter(
            user=user, is_active=True, site=identifier
        ).first()
        return user_key

    # Handle as program/observation ID.
    try:
        gemini_id = GeminiID(identifier)
    except ValueError:
        return None

    # Attempt to retrieve a ProgramKey.
    program_key = ProgramKey.objects.filter(
        user=user, program_id=gemini_id.program_id, site=gemini_id.site
    ).first()
    return program_key


def get_key_info(user: User, identifier: str) -> dict[str, str]:
    """Generates a dictionary of key information used for observation payload.

    Parameters
    ----------
    user : `User`
        The user the key belongs to.
    identifier : `str`
        The site (GN/GS) or the program/observation ID.

    Returns
    -------
    `dict[str, str]`
        A payload meant to be merged with the observation payload.
    """
    key = get_key(user, identifier=identifier)
    if key is None:
        return {}

    # Build key info.
    key_info = {"password": key.password}

    if isinstance(key, UserKey):
        key_info["email"] = key.email

    return key_info


def has_key(user: User, identifier: str) -> bool:
    """Checks if a key exists for a user for either a site or a
    program/observation ID.

    Parameters
    ----------
    user : `User`
        The user the key belongs to.
    identifier : `str`
        The site (GN/GS) or the program/observation ID.

    Returns
    -------
    `bool`
        `True` if a key exists, `False` otherwise.
    """
    if identifier in GeminiID.sites:
        # Check for the existence of an active UserKey for the site.
        user_key_exists = UserKey.objects.filter(
            user=user, is_active=True, site=identifier
        ).exists()
        return user_key_exists

    # Handle as program/observation ID.
    try:
        gemini_id = GeminiID(identifier)
    except ValueError:
        return False

    # Check for the existence of a ProgramKey.
    program_key_exists = ProgramKey.objects.filter(
        user=user, program_id=gemini_id.program_id, site=gemini_id.site
    ).exists()
    return program_key_exists
