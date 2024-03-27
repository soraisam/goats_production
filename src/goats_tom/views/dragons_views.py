"""Views for DRAGONS operations."""

__all__ = [
    "DRAGONSSetupAPIView",
    "DRAGONSView",
    "DRAGONSFileListView",
]

import hashlib
from collections import defaultdict
from pathlib import Path

import astrodata
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from goats_tom.models import DRAGONSFileMetadata, DRAGONSRun
from goats_tom.serializers import DRAGONSFileMetadataSerializer, DRAGONSRunSerializer
from recipe_system import cal_service
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tom_observations.models import ObservationRecord


class DRAGONSView(LoginRequiredMixin, View):
    """A Django view for displaying the DRAGONS page."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Handles GET requests to display DRAGONS.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.
        pk : `int`
            The primary key of the `ObservationRecord`.

        Returns
        -------
        `HttpResponse`
            The rendered DRAGONS page.
        """
        observation_record = get_object_or_404(ObservationRecord, pk=pk)
        dragons_runs = observation_record.dragons_runs.all()

        # Get the available folders for display.
        return render(
            request,
            "dragons_index.html",
            {"observation_record": observation_record, "dragons_runs": dragons_runs},
        )


class DRAGONSSetupAPIView(APIView):
    """A Django REST Framework view for retrieving and setting up DRAGONS runs.

    Supports GET requests to list DRAGONS runs associated with an
    `ObservationRecord`, and POST requests to create a new DRAGONS run.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        """Handles GET requests, returning a list of DRAGONS runs for a
        given `ObservationRecord`.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.
        pk : `int`
            The primary key of the `ObservationRecord` whose DRAGONS runs
            are to be listed.

        Returns
        -------
        `Response`
            A response containing the list of DRAGONS runs or an error message.
        """
        try:
            observation_record = ObservationRecord.objects.get(pk=pk)

        except ObservationRecord.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "errors": ["Observation record does not exist."],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the queryset of related DRAGONS runs.
        dragons_runs = observation_record.dragons_runs.all()
        serializer = DRAGONSRunSerializer(dragons_runs, many=True)

        # Include the serialized data in your response.
        return Response({"success": True, "dragons_runs": serializer.data})

    def post(self, request: HttpRequest, pk: str, *args, **kwargs) -> Response:
        """Handles POST requests to create a new DRAGONS run setup.

        Parameters
        ----------
        request : `HttpRequest`
            The request object containing the setup data.
        pk : `int`
            The primary key of the ObservationRecord for which the DRAGONS run
            is created.

        Returns
        -------
        `Response`
            A response indicating the success or failure of the DRAGONS run
            setup.
        """
        print(request.data)
        serializer = DRAGONSRunSerializer(data=request.data)
        if serializer.is_valid():
            dragons_run = serializer.save()

            try:
                observation_record = ObservationRecord.objects.get(pk=pk)
            except ObservationRecord.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "errors": ["Observation record does not exist."],
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Create the output directory.
            output_dir = dragons_run.get_output_dir()
            output_dir.mkdir(parents=True)

            cal_manager_db_file = output_dir / "cal_manager.db"
            dragons_rc_file = output_dir / "dragonsrc"

            # Write the DRAGONS config file.
            with dragons_rc_file.open("w") as f:
                f.write(f"[calibs]\ndatabases = {cal_manager_db_file} get store")

            # Create the calibration manager for DRAGONS.
            cal_service.LocalDB(cal_manager_db_file, force_init=True)

            # Return all runs in payload.
            dragons_runs = observation_record.dragons_runs.all()
            serializer = DRAGONSRunSerializer(dragons_runs, many=True)

            return Response(
                {
                    "success": True,
                    "dragons_runs": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        print(serializer.errors)
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


def calculate_directory_hash(directory: Path) -> str:
    hash_sha256 = hashlib.sha256()
    for path in sorted(directory.glob("*.fits")):
        hash_sha256.update(str(path.name).encode() + str(path.stat().st_mtime).encode())
    return hash_sha256.hexdigest()


class DRAGONSFileListView(APIView):

    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
        sort_by_file_type = serializers.BooleanField(required=False)

    def patch(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        """Handles partial updates to the `DRAGONSFileMetadata` instance
        identified by the primary key.

        Parameters
        ----------
        request : `HttpRequest`
            The request object containing the partial data to update.
        pk : `int`
            The primary key of the `DRAGONSFileMetadata` instance to update.

        Returns
        -------
        `Response`
            A response object containing the updated metadata on success,
            or an error message on failure.
        """
        # Fetch the existing instance to update.
        file_metadata_instance = get_object_or_404(DRAGONSFileMetadata, pk=pk)

        # Initialize the serializer with the instance and request data for
        # partial update.
        serializer = DRAGONSFileMetadataSerializer(
            instance=file_metadata_instance,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"success": True, "dragons_files_metadata": serializer.data}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400,  # Bad request status
        )

    def get(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        """Retrieves and updates the file metadata for a DRAGONS run based on
        the directory hash comparison.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.
        pk : `int`
            The primary key of the DRAGONSRun instance to retrieve.

        Returns
        -------
        `Response`
            Response containing serialized DRAGONS file metadata.
        """
        dragons_run = get_object_or_404(DRAGONSRun, pk=pk)
        raw_dir = dragons_run.get_raw_dir()
        current_hash = calculate_directory_hash(raw_dir)

        # Check if directory hash has changed indicating updates are necessary.
        if dragons_run.directory_hash != current_hash:
            # TODO: Convert to background task.
            print("Redoing directory file metadata.")
            existing_files = {
                metadata.filename: metadata
                for metadata in dragons_run.files_metadata.all()
            }
            all_files = [file for file in raw_dir.glob("*.fits")]

            # Update existing metadata and track files processed.
            processed_files = set()

            for file_path in all_files:
                filename = file_path.name
                processed_files.add(filename)

                metadata = existing_files.pop(filename, None)
                file_metadata = extract_metadata(file_path)

                # Skip if prepared file.
                if file_metadata is None:
                    continue

                if metadata:
                    # Update existing metadata with new values.
                    for key, value in file_metadata.items():
                        setattr(metadata, key, value)
                    metadata.save()
                else:
                    # Create new metadata for new files found in the directory.
                    DRAGONSFileMetadata.objects.create(
                        dragons_run=dragons_run, **file_metadata
                    )

            # Any remaining entries in existing_files are no longer present and
            # should be handled accordingly
            for metadata in existing_files.values():
                # Mark as archived since file deleted and disable.
                metadata.archived = True
                metadata.enabled = False
                metadata.save()

            # Update the directory hash to reflect current state.
            dragons_run.directory_hash = current_hash
            dragons_run.save()

        filter_serializer = self.FilterSerializer(data=request.query_params)

        # Don't raise error since not critical.
        filter_serializer.is_valid(raise_exception=False)

        # Serialize the updated or existing file metadata for response.
        serializer = DRAGONSFileMetadataSerializer(
            dragons_run.files_metadata.all(), many=True
        )

        if filter_serializer.validated_data["sort_by_file_type"]:
            # Reformat the serialized data to be grouped by 'file_type'.
            grouped_by_file_type = defaultdict(list)
            for item in serializer.data:
                grouped_by_file_type[(item["file_type"]).lower()].append(item)
            data = dict(grouped_by_file_type)
        else:
            data = serializer.data

        return Response({"success": True, "dragons_files_metadata": data})


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
    and observation classes present in the file's metadata. Currently handles
    "BIAS", "DARK", "FLAT", "ARC", "PINHOLE", "RONCHI", "FRINGE", and
    "standard" file types, with a fallback to "unknown" or "object" types based
    on observation class.
    """
    # Define calibration file tags for identification.
    cal_file_tags = ["BIAS", "DARK", "FLAT", "ARC", "PINHOLE", "RONCHI", "FRINGE"]

    # Open the file using astrodata.
    ad = astrodata.open(file_path)

    # Determine file type based on tags and observation class.
    file_type = "unknown"
    if "BPM" in ad.tags:
        file_type = "BPM"
    elif "PREPARED" in ad.tags:
        # Skip files marked as "PREPARED".
        return None
    elif (
        (
            "STANDARD" in ad.tags
            or ad.observation_class() == "partnerCal"
            or ad.observation_class() == "progCal"
        )
        and "UNPREPARED" in ad.tags
        and ad.observation_type() == "OBJECT"
    ):
        file_type = "standard"
    elif "CAL" in ad.tags and "UNPREPARED" in ad.tags:
        # Check against a list of calibration file tags.
        for tag in cal_file_tags:
            if tag in ad.tags:
                file_type = tag
                break
    elif ad.observation_class() == "science" and "UNPREPARED" in ad.tags:
        file_type = "object"

    # Construct the metadata dictionary.
    metadata_dict = {
        "file_type": file_type,
        "filename": file_path.name,
        "group_id": (
            ad.group_id() if "GNIRS" not in ad.instrument() else None
        ),  # GNIRS not implemented yet with groups.
        "exposure_time": ad.exposure_time(),
        "object_name": ad.object(),
        "central_wavelength": ad.central_wavelength(),
        "wavelength_band": ad.wavelength_band(),
        "observation_date": ad.ut_date().isoformat(),
        "roi_setting": ad.detector_roi_setting(),
        "enabled": True,
        "archived": False,
    }

    return metadata_dict
