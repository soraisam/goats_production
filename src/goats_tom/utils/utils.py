"""Utility functions."""

__all__ = [
    "delete_associated_data_products",
    "create_name_reduction_map",
    "custom_data_product_path",
    "build_json_response",
    "get_key",
    "has_key",
    "get_key_info",
    "extract_metadata",
    "get_short_name",
    "get_astrodata_header",
    "get_recipes_and_primitives",
]

import importlib
import inspect
import re
from pathlib import Path
from typing import Any

import astrodata
from astropy.table import Table
from django.contrib.auth.models import User
from django.http import JsonResponse
from recipe_system.mappers.recipeMapper import RecipeMapper
from recipe_system.utils.errors import ModeError, RecipeNotFound
from rest_framework import status
from tom_dataproducts.models import DataProduct, ReducedDatum
from tom_observations.models import ObservationRecord

from goats_tom.models import ProgramKey, UserKey
from goats_tom.ocs import GeminiID


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
            "Invalid argument type. Must be ObservationRecord or DataProduct.",
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

    return f"{data_product.target.name}/none/none/{filename}"


def build_json_response(
    error_message: str | None = None,
    error_status: int | None = status.HTTP_200_OK,
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
            {"status": "error", "message": error_message},
            status=error_status,
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
            user=user,
            is_active=True,
            site=identifier,
        ).first()
        return user_key

    # Handle as program/observation ID.
    try:
        gemini_id = GeminiID(identifier)
    except ValueError:
        return None

    # Attempt to retrieve a ProgramKey.
    program_key = ProgramKey.objects.filter(
        user=user,
        program_id=gemini_id.program_id,
        site=gemini_id.site,
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
            user=user,
            is_active=True,
            site=identifier,
        ).exists()
        return user_key_exists

    # Handle as program/observation ID.
    try:
        gemini_id = GeminiID(identifier)
    except ValueError:
        return False

    # Check for the existence of a ProgramKey.
    program_key_exists = ProgramKey.objects.filter(
        user=user,
        program_id=gemini_id.program_id,
        site=gemini_id.site,
    ).exists()
    return program_key_exists


def extract_metadata(file_path: Path) -> dict | None:
    """Extract metadata from a file using astrodata.

    Parameters
    ----------
    file_path : `Path`
        The path to the file from which to extract metadata.

    Returns
    -------
    `dict | None`
        A dictionary containing extracted metadata, or `None` if the file is
        marked as "PREPARED" or does not meet criteria for metadata extraction.

    Notes
    -----
    This function utilizes the astrodata library to open and extract relevant
    metadata from files. It identifies the file type based on specific tags
    and observation classes present in the file's metadata.

    """
    # Open the file using astrodata.
    ad = astrodata.open(file_path)

    # Only want unprepared or BPM files.
    if "BPM" in ad.tags or "UNPREPARED" in ad.tags:
        # Skip all prepared and processed files.
        if "PREPARED" in ad.tags or "PROCESSED" in ad.tags:
            return
        # Construct the metadata dictionary.
        metadata_dict = {
            "observation_type": ad.observation_type(),
            # "observation_class", ad.observation_class(),
            "group_id": (
                ad.group_id() if "GNIRS" not in ad.instrument() else None
            ),  # GNIRS not implemented yet with groups.
            "exposure_time": ad.exposure_time(),
            "object_name": ad.object(),
            "central_wavelength": ad.central_wavelength(),
            "wavelength_band": ad.wavelength_band(),
            "observation_date": ad.ut_date().isoformat(),
            "roi_setting": ad.detector_roi_setting(),
            "instrument": ad.instrument(generic=True).lower(),
            "tags": list(ad.tags),
        }

        return metadata_dict
    return


def get_short_name(name: str) -> str | None:
    """Extracts the short name from the recipe's full name.

    Returns
    -------
    `str | None`
        The short name extracted after "::" if present.

    """
    # Regular expression pattern to capture text after "::".
    pattern = r"::(\w+)$"
    # Using re.search to find the match.
    match = re.search(pattern, name)
    if match:
        return match.group(1)
    return None


def get_astrodata_header(data_product: DataProduct) -> dict[str, Any]:
    """Gets the header information from astrodata.

    Parameters
    ----------
    data_product : `DataProduct`
        The data product to extract headers.

    Returns
    -------
    `dict[str, Any]`
        Header payload from astrodata.

    """
    ad = astrodata.open(data_product.data.path)
    # Prepare the header information.
    header = {}
    for descriptor in ad.descriptors:
        # Fetch the value of the descriptor.
        value = getattr(ad, descriptor)()

        # Append the descriptor data to the header list.
        header[descriptor] = value

    return header


def get_recipes_and_primitives(tags: set, instrument: str) -> dict[str, Any]:
    """Retrieves all applicable recipes and their associated primitives based on the
    given tags and instrument. It also determines which recipe should be considered the
    default for the given parameters.

    Parameters
    ----------
    tags : `set`
        A set of tags associated with the file, used to identify applicable recipes.
    instrument : `str`
        The instrument type, used to filter recipes specific to the instrument.

    Returns
    -------
    `dict[str, Any]`
        A dictionary containing recipes keyed by their names, each with details such as
        the recipe's function definition, module, and whether it is the default recipe.

    Raises
    ------
    RecipeNotFound, ModeError
        Raised if no applicable recipe is found or there's an error in processing modes.
    """
    recipes = {}

    # Attempt to get recipes for just "sq" for GOATS.
    for mode in ["sq"]:
        try:
            recipe_mapper = RecipeMapper(tags, instrument, mode=mode)
            applicable_recipe = recipe_mapper.get_applicable_recipe()
            module = importlib.import_module(applicable_recipe.__module__)
            # Loop through and build the recipe function definition from primitives.
            for func_name, func in inspect.getmembers(
                module,
                inspect.isfunction,
            ):
                if func_name == "_default":
                    # Skip the default as this is listed twice if it is included.
                    continue

                recipe_name = f"{func.__module__}::{func.__name__}"
                recipe_module = f"{func.__module__.split('.')[-1]}"
                # Want to skip common as they are just to be shared between recipe
                # modules.
                if recipe_module == "recipes_common":
                    continue

                source_code = inspect.getsource(func)
                primitives = re.findall(r"p\..*", source_code)

                # Construct the function definition for the recipe.
                function_definition = _create_recipe_function_definition(
                    func.__name__,
                    primitives,
                )
                is_default = func.__name__ == applicable_recipe.__name__

                recipes[recipe_name] = {
                    "function_definition": function_definition,
                    "is_default": is_default,
                    "recipes_module": recipe_module,
                }

        except (RecipeNotFound, ModeError) as e:
            print(f"Error parsing recipes and primitives: {e}")
            continue

    return {"recipes": recipes}


def _create_recipe_function_definition(recipe_name: str, primitives: list[str]) -> str:
    """Constructs a Python function definition string from a list of primitive
    operations.

    Parameters
    ----------
    recipe_name : `str`
        The name of the recipe function to be defined.
    primitives : `list[str]`
        A list of string representations of primitive operations that form the body of
        the function.

    Returns
    -------
    `str`
        A formatted string representing the complete Python function definition.

    """
    function_body = "\n".join(f"    {primitive.strip()}" for primitive in primitives)
    return f"def {recipe_name}(p):\n{function_body}\n"
