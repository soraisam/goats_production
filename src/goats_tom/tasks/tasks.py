__all__ = ["download_goa_files"]

import logging
import time

from django.conf import settings
from django.core import serializers
from django.db import IntegrityError
from huey.contrib.djhuey import db_task
from requests.exceptions import HTTPError
from tom_dataproducts.models import DataProduct

from goats_tom.astroquery import Observations as GOA
from goats_tom.consumers import DownloadState, NotificationInstance
from goats_tom.models import DataProductMetadata, Download, GOALogin
from goats_tom.utils import create_name_reduction_map, extract_metadata

logger = logging.getLogger(__name__)


@db_task()
def download_goa_files(serialized_observation_record, query_params, user: int):
    # Allow page to refresh before displaying notification.
    print("Running background task.")
    time.sleep(2)

    download_state = DownloadState()

    # Only ever one observation record passed.
    observation_record = list(
        serializers.deserialize("json", serialized_observation_record)
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
        message="Download started.", label=f"{observation_id}"
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
        logger.warning(f"GOA login failed. Re-enter login credentials. {prop_data_msg}")

    # Get target path.
    target_facility_path = settings.MEDIA_ROOT / target.name / facility / observation_id

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
    try:
        sci_files = []
        cal_files = []

        # Query GOA for science tarfile.
        if not download_calibration == "only":
            print(f"{observation_id}: Downloading science files...")

            download_state.update_and_send(
                status="Downloading science files...", downloaded_bytes=0
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

        if not download_calibration == "no":
            print(f"{observation_id}: Downloading calibration files...")
            download_state.update_and_send(
                status="Downloading calibration files...", downloaded_bytes=0
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
            status="Finished downloads...", downloaded_bytes=None
        )

    except HTTPError as e:
        if e.response.status_code == 403:
            logger.error("You are not authorized to download this data.")
        else:
            logger.error("HTTP Error occured: %s", e)

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
        # Extract and save the metadata
        # TODO: Will this ever be empty?
        metadata = extract_metadata(file_path)
        DataProductMetadata.objects.update_or_create(data_product=dp, defaults=metadata)

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
        message=f"{message}", label=f"{observation_id}", color="success"
    )
