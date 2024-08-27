"""Module for tasks that run in the background."""

__all__ = ["download_goa_files", "run_dragons_reduce"]

import logging
import os
import sys
import time
import types
import uuid

import dramatiq
import matplotlib
from django.conf import settings
from django.core import serializers
from django.db import IntegrityError
from gempy.utils import logutils
from recipe_system.reduction.coreReduce import Reduce
from requests.exceptions import HTTPError
from tom_dataproducts.models import DataProduct

from goats_tom.astroquery import Observations as GOA
from goats_tom.logging.handlers import DRAGONSHandler
from goats_tom.models import (
    Download,
    DRAGONSReduce,
    GOALogin,
)
from goats_tom.realtime import DownloadState, DRAGONSProgress, NotificationInstance
from goats_tom.utils import create_name_reduction_map

matplotlib.use("Agg", force=True)

logger = logging.getLogger(__name__)


@dramatiq.actor(max_retries=0)
def run_dragons_reduce(reduce_id: int, file_ids: list[int]) -> None:
    """Executes a reduction process in the background.

    This function handles the entire process of setting up and executing a reduction,
    including notification handling, file management, and executing the reduction logic.

    Parameters
    ----------
    reduce_id : `int`
        The ID of the DRAGONSReduce instance to be processed.
    file_ids : `list[int]`
        A list of file IDs to limit to. If empty, use all files.

    Raises
    ------
    `DoesNotExist`
        Raised if the DRAGONSReduce instance does not exist.

    """
    try:
        # Get the reduction to run in the background.
        print("Running background reduce task.")
        # Get the recipe instance.
        reduce = DRAGONSReduce.objects.get(id=reduce_id)

        run = reduce.recipe.dragons_run
        recipe = reduce.recipe
        recipes_module = recipe.recipe.recipes_module
        # Send start notification.
        NotificationInstance.create_and_send(
            message="Reduction started.",
            label=reduce.get_label(),
        )
        reduce.mark_initializing()
        DRAGONSProgress.create_and_send(reduce)

        time.sleep(2)

        # Create an instance of the custom handler.
        dragons_handler = DRAGONSHandler(
            recipe_id=recipe.id,
            reduce_id=reduce.id,
            run_id=run.id,
        )
        dragons_handler.setLevel(21)

        # Change the working directory to save outputs.
        os.chdir(run.get_output_dir())

        # Filter the files based on the associated DRAGONS run and file type.
        if file_ids:
            files = recipes_module.files.filter(
                enabled=True, dragons_run=run, id__in=file_ids
            )
        else:
            files = recipes_module.files.filter(enabled=True, dragons_run=run)
        file_paths = [file.file_path for file in files]

        # Setup the logger.
        logutils.config(
            mode="standard",
            file_name=run.log_filename,
            additional_handlers=dragons_handler,
        )

        r = Reduce()

        # Get error if passing in Path.
        r.config_file = str(run.get_config_file())

        r.files.extend(file_paths)

        # Prepare a namespace to execute the user-provided function definition safely.
        function_definition_namespace = {}

        # Execute the function definition provided by the user.
        exec(recipe.active_function_definition, {}, function_definition_namespace)

        # Search through the namespace to find any callable defined therein.
        function_definition = None
        for _, obj in function_definition_namespace.items():
            if callable(obj):
                function_definition = obj
                break

        # Ensure a function was successfully defined and retrieved.
        if function_definition is None:
            raise ValueError("No recipe was defined in the provided recipe.")

        # Generate a unique module name to avoid conflicts in sys.modules.
        unique_id = uuid.uuid4()
        module_name = f"dynamic_recipes_{unique_id}"

        # Create a new module and add it to `sys.modules`.
        recipe_module = types.ModuleType(module_name)
        sys.modules[module_name] = recipe_module

        # Add the user-defined function to the newly created module.
        setattr(recipe_module, function_definition.__name__, function_definition)

        # Format the recipename to be recognized by DRAGONS which expects
        # "<module_name>.<function_name>".
        r.recipename = f"{module_name}.{function_definition.__name__}"

        reduce.mark_running()
        DRAGONSProgress.create_and_send(reduce)

        r.runr()

        # Send finished notification.
        NotificationInstance.create_and_send(
            message="Reduction finished.",
            label=reduce.get_label(),
            color="success",
        )
        reduce.mark_done()
        DRAGONSProgress.create_and_send(reduce)

    except DRAGONSReduce.DoesNotExist:
        # Send error to frontend.
        NotificationInstance.create_and_send(
            message="Reduction not found.",
            color="danger",
        )
        raise
    except Exception as e:
        # Catch all other exceptions.
        reduce.mark_error()
        DRAGONSProgress.create_and_send(reduce)
        NotificationInstance.create_and_send(
            label=reduce.get_label(),
            message=f"Error during reduction: {e!s}",
            color="danger",
        )
        raise
    finally:
        # Cleanup dynamically created module.
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"Module {module_name} removed from sys.modules.")


@dramatiq.actor(max_retries=0)
def download_goa_files(
    serialized_observation_record: str,
    query_params: dict,
    user: int,
) -> None:
    """Downloads observation files associated with a given observation record from the
    GOA.

    This task logs in to the GOA, queries for relevant files based on the provided
    observation record, and handles the download and metadata extraction for each file.
    Notifications are sent at various stages of the process to update the user on the
    task status.

    Parameters
    ----------
    serialized_observation_record : `str`
        A JSON serialized string of the observation record object.
    query_params : `dict`
        A dictionary containing additional parameters for querying and downloading
        files.
    user : `int`
        The user ID used to retrieve credentials for accessing the GOA.

    Raises
    ------
    `PermissionError`
        Raised if the GOA login fails due to incorrect credentials.
    `HTTPError`
        Raised if an HTTP error occurs during the download process.

    """
    try:
        # Allow page to refresh before displaying notification.
        print("Running background task.")
        time.sleep(2)

        download_state = DownloadState()

        # Only ever one observation record passed.
        observation_record = list(
            serializers.deserialize("json", serialized_observation_record),
        )[0].object
        target = observation_record.target
        facility = observation_record.facility
        observation_id = observation_record.observation_id

        # Create Download record at the start
        download = Download.objects.create(
            observation_id=observation_id,
            status="Running",
            unique_id=download_state.unique_id,
        )

        NotificationInstance.create_and_send(
            message="Download started.",
            label=f"{observation_id}",
        )
        download_state.update_and_send(label=observation_id, status="Starting...")

        # Have to handle logging in for each task.
        prop_data_msg = "Proprietary data will not be downloaded."
        try:
            goa_credentials = GOALogin.objects.get(user=user)
            # Login to GOA.
            GOA.login(goa_credentials.username, goa_credentials.password)

            if not GOA.authenticated():
                raise PermissionError
        except GOALogin.DoesNotExist:
            logger.warning(f"GOA login credentials not found. {prop_data_msg}")
        except PermissionError:
            logger.warning(
                f"GOA login failed. Re-enter login credentials. {prop_data_msg}"
            )

        # Get target path.
        target_facility_path = (
            settings.MEDIA_ROOT / target.name / facility / observation_id
        )

        # Set default args and kwargs if not provided in query_params.
        args = query_params.get("args", ())
        kwargs = query_params.get("kwargs", {})

        # Pass in the observation ID to query only for this observation.
        kwargs["progid"] = observation_id

        # Determine what to do with calibration data.
        download_calibration = kwargs.pop("download_calibrations", None)

        # Create blank mapping.
        name_reduction_map = {}
        num_files_omitted = 0
        sci_files = []
        cal_files = []

        # Query GOA for science tarfile.
        if download_calibration != "only":
            print(f"{observation_id}: Downloading science files...")

            download_state.update_and_send(
                status="Downloading science files...",
                downloaded_bytes=0,
            )

            file_list = GOA.query_criteria(*args, **kwargs)
            # Create the mapping.
            name_reduction_map = create_name_reduction_map(file_list)
            sci_out = GOA.get_files(
                target_facility_path,
                *args,
                decompress_fits=True,
                download_state=download_state,
                **kwargs,
            )
            sci_files = sci_out["downloaded_files"]
            num_files_omitted += sci_out["num_files_omitted"]

        if download_calibration != "no":
            print(f"{observation_id}: Downloading calibration files...")
            download_state.update_and_send(
                status="Downloading calibration files...",
                downloaded_bytes=0,
            )

            # Query GOA for calibration tarfile.
            # Only need to specify program ID.
            calibration_kwargs = {"progid": observation_id}
            cal_out = GOA.get_calibration_files(
                target_facility_path,
                *args,
                decompress_fits=True,
                download_state=download_state,
                **calibration_kwargs,
            )
            cal_files = cal_out["downloaded_files"]
            num_files_omitted += cal_out["num_files_omitted"]

        download_state.update_and_send(
            status="Finished downloads...",
            downloaded_bytes=None,
        )

        # Handle case if GOA found nothing and did not create folder.
        if not target_facility_path.exists():
            download.finish()
            return

        downloaded_files = set(sci_files + cal_files)
        num_files_downloaded = len(downloaded_files)

        # Now lead by the files in the folder.
        for file_name in downloaded_files:
            file_path = target_facility_path / file_name
            if file_path.suffix != ".fits":
                continue

            product_id = file_path.stem

            # Use the mapping to get the data product type.
            # If not found, return default for calibration.
            data_product_type = name_reduction_map.get(file_path.name, "RAW")
            # Query DataProduct by product_id.
            candidates = DataProduct.objects.filter(
                product_id=product_id,
                observation_record=observation_record,
                target=target,
            )

            if candidates.exists():
                # If we have candidates, just grab the first one.
                dp = candidates.first()
            else:
                # Otherwise, create a new DataProduct.
                try:
                    data_product_name = (
                        f"{target.name}/{facility}/{observation_id}/{file_path.name}"
                    )
                    dp = DataProduct.objects.create(
                        product_id=product_id,
                        target=target,
                        observation_record=observation_record,
                        data_product_type=data_product_type,
                    )
                    dp.data.name = data_product_name
                    dp.save()
                    logger.info("Saved new dataproduct from tarfile: %s", dp.data)
                except IntegrityError:
                    logger.error(
                        "There already exists a data product '%s', skipping.",
                        file_path.name,
                    )

        GOA.logout()

        # Update downloaded and omitted data.
        download.num_files_downloaded = num_files_downloaded
        download.num_files_omitted = num_files_omitted
        download.finish()
        download_state.update_and_send(status="Done.", done=True)

        # Build message for notificaiton.
        message = f"Downloaded {num_files_downloaded} files."
        if num_files_omitted > 0:
            message += f" {num_files_omitted} proprietary files were omitted."

        NotificationInstance.create_and_send(
            message=f"{message}",
            label=f"{observation_id}",
            color="success",
        )
        print("Done.")
    except HTTPError as e:
        download.finish(message=str(e), error=True)
        download_state.update_and_send(status="Failed.", error=True)
        NotificationInstance.create_and_send(
            message=f"Connection to GOA failed, cannot download files: {e!s}",
            color="danger",
        )
        raise
    except Exception as e:
        # Catch all other exceptions.
        download.finish(message=str(e), error=True)
        download_state.update_and_send(status="Failed.", error=True)
        NotificationInstance.create_and_send(
            message=f"Error during download from GOA: {e!s}",
            color="danger",
        )
        raise
