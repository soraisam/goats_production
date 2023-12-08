from pathlib import Path
import logging
from requests.exceptions import HTTPError

from django.conf import settings
from django.core import serializers
from huey.contrib.djhuey import db_task

from tom_dataproducts.models import DataProduct
from .astroquery_gemini import Observations as GOA
from .utils import create_name_reduction_map
from .models import GOALogin, TaskProgress

logger = logging.getLogger(__name__)


@db_task()
def download_goa_files(serialized_observation_record, query_params, user: int):
    # Only ever one observation record passed.
    observation_record = list(serializers.deserialize("json", serialized_observation_record))[0].object
    target = observation_record.target
    facility = observation_record.facility
    # Create TaskProgress record at the start
    task_progress = TaskProgress.objects.create(
        task_id=observation_record.observation_id,
        progress=1,
        status="running",
    )

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
    target_path = Path(f"{settings.MEDIA_ROOT}/{target.name}")
    target_facility_path = target_path / facility

    # Set default args and kwargs if not provided in query_params.
    args = query_params.get("args", ())
    kwargs = query_params.get("kwargs", {})

    # Pass in the observation ID to query only for this observation.
    kwargs["progid"] = observation_record.observation_id

    # Determine what to do with calibration data.
    download_calibration = kwargs.pop("download_calibrations", None)

    # Create blank mapping.
    name_reduction_map = {}
    try:
        sci_files = []
        cal_files = []

        # Query GOA for science tarfile.
        if not download_calibration == "only":
            print(f"{observation_record.observation_id}: Downloading science files...")
            file_list = GOA.query_criteria(*args, **kwargs)
            # Create the mapping.
            name_reduction_map = create_name_reduction_map(file_list)
            sci_out = GOA.get_files(target_path, *args, extract_dir=target_facility_path,
                                    decompress_fits=True, **kwargs)
            sci_files = sci_out["downloaded_files"]
            task_progress.progress += 45
            task_progress.save()

        if not download_calibration == "no":
            print(f"{observation_record.observation_id}: Downloading calibration files...")
            # Query GOA for calibration tarfile.
            # Only need to specify program ID.
            calibration_kwargs = {"progid": observation_record.observation_id}
            cal_out = GOA.get_calibration_files(target_path, *args, extract_dir=target_facility_path,
                                                decompress_fits=True,
                                                **calibration_kwargs)
            cal_files = cal_out["downloaded_files"]

        task_progress.progress = 90
        task_progress.save()

    except HTTPError as e:
        if e.response.status_code == 403:
            logger.error("You are not authorized to download this data.")
        else:
            logger.error("HTTP Error occured: %s", e)

    # Handle case if GOA found nothing and did not create folder.
    if not target_facility_path.exists():
        task_progress.finish()
        return

    downloaded_files = sci_files + cal_files
    # Now lead by the files in the folder.
    for file_name in downloaded_files:
        file_path = target_facility_path / file_name
        if file_path.suffix != ".fits":
            continue

        product_id = file_path.stem

        # Use the mapping to get the data product type.
        # If not found, return default for calibration.
        data_product_type = name_reduction_map.get(file_path.name, "RAW")
        # Query DataProduct by product_id and target.
        candidates = DataProduct.objects.filter(product_id=product_id, target=target)

        if candidates.exists():
            # If we have candidates, just grab the first one.
            dp = candidates.first()
        else:
            # Otherwise, create a new DataProduct.
            data_product_name = f"{target.name}/{facility}/{file_path.name}"
            dp = DataProduct.objects.create(
                product_id=product_id,
                target=target,
                observation_record=observation_record,
                data_product_type=data_product_type
            )
            dp.data.name = data_product_name
            dp.save()
            logger.info("Saved new dataproduct from tarfile: %s", dp.data)

    GOA.logout()
    task_progress.finish()
