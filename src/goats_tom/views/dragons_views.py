"""Views for DRAGONS operations."""

__all__ = [
    "DRAGONSRunsAPIView",
    "DRAGONSView",
    "DRAGONSFilesAPIView",
    "DRAGONSRunDataProductAPIView",
]

from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from recipe_system import cal_service
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tom_dataproducts.models import DataProduct
from tom_observations.models import ObservationRecord

from goats_tom.models import DRAGONSRunDataProduct
from goats_tom.serializers import DRAGONSRunSerializer


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


class DRAGONSRunsAPIView(APIView):
    """A Django REST Framework view for retrieving and setting up DRAGONS runs.

    Supports GET requests to list DRAGONS runs associated with an
    `ObservationRecord`, and POST requests to create a new DRAGONS run.
    """

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request: HttpRequest,
        observation_record_pk: int,
        *args,
        **kwargs,
    ) -> Response:
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
        # Retrieve the observation record and dragons run instances.
        observation_record = get_object_or_404(
            ObservationRecord, pk=observation_record_pk
        )

        # Serialize the queryset of related DRAGONS runs.
        dragons_runs = observation_record.dragons_runs.all()
        serializer = DRAGONSRunSerializer(dragons_runs, many=True)

        # Include the serialized data in your response.
        return Response({"success": True, "runs": serializer.data})

    def post(
        self, request: HttpRequest, observation_record_pk: str, *args, **kwargs
    ) -> Response:
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
        serializer = DRAGONSRunSerializer(data=request.data)
        if serializer.is_valid():
            dragons_run = serializer.save()

            observation_record = get_object_or_404(
                ObservationRecord, pk=observation_record_pk
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

            # Fetch all DataProducts associated with the observation record.
            data_products = DataProduct.objects.filter(
                observation_record=observation_record
            )

            # For each DataProduct, link it to the DRAGONS run as enabled.
            for dp in data_products:
                DRAGONSRunDataProduct.objects.update_or_create(
                    dragons_run=dragons_run, data_product=dp, defaults={"enabled": True}
                )

            return Response(
                {
                    "success": True,
                    "message": "Created run and linked associated data products.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DRAGONSFilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
        sort_by_file_type = serializers.BooleanField(required=False)

    def get(
        self,
        request: HttpRequest,
        observation_record_pk: int,
        dragons_run_pk: int,
        *args,
        **kwargs,
    ) -> Response:
        """
        Retrieves and serializes `DataProduct` information associated with a
        specific `ObservationRecord` and `DRAGONSRun`.

        This method optimizes database queries by using "select_related" to
        prefetch related `DataProduct` and `DataProductMetadata` in a single
        query.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.
        observation_record_pk : `int`
            The primary key of the `ObservationRecord`.
        dragons_run_pk : `int`
            The primary key of the `DRAGONSRun`.

        Returns
        -------
        `Response`
            A serialized response containing data product information.
        """
        # Fetch the linked DRAGONSRunDataProduct entries
        dragons_run_data_products = DRAGONSRunDataProduct.objects.filter(
            dragons_run_id=dragons_run_pk,
        ).select_related("data_product__observation_record", "data_product__metadata")

        filter_serializer = self.FilterSerializer(data=request.query_params)

        # Don't raise error since not critical.
        filter_serializer.is_valid(raise_exception=False)

        # Serialize the data
        serializer = DRAGONSRunDataProductSerializer(
            dragons_run_data_products, many=True
        )

        if filter_serializer.validated_data["sort_by_file_type"]:
            # Reformat the serialized data to be grouped by 'file_type'.
            grouped_by_file_type = defaultdict(list)
            for item in serializer.data:
                grouped_by_file_type[(item["file_type"]).lower()].append(item)
            data = dict(grouped_by_file_type)
        else:
            data = serializer.data

        return Response({"success": True, "dragons_files": data})


class DRAGONSRunDataProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        """Serializer for input validation of "PATCH" DRAGONSRunDataProduct.

        Attributes
        ----------
        enabled : `serializers.BooleanField`
            A boolean field to specify whether the data product is enabled.
        """

        enabled = serializers.BooleanField()

    def patch(
        self,
        request,
        observation_record_pk,
        dragons_run_pk,
        dragons_run_data_product_pk,
        *args,
        **kwargs,
    ):
        """Updates the state of a `DRAGONSRunDataProduct`.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.
        observation_record_pk : `int`
            The primary key of the ObservationRecord.
        dragons_run_pk : `int`
            The primary key of the DRAGONSRun.
        dragons_run_data_product_pk : `int`
            The primary key of the DRAGONSRunDataProduct to be updated.

        Returns
        -------
        `Response`
            The response object with success message or errors.
        """
        dragons_run_data_product = get_object_or_404(
            DRAGONSRunDataProduct, pk=dragons_run_data_product_pk
        )

        # Load body in serializer.
        input_serializer = self.InputSerializer(data=request.data)

        if input_serializer.is_valid():
            dragons_run_data_product.enabled = input_serializer.validated_data[
                "enabled"
            ]
            dragons_run_data_product.save()

            return Response({"success": True, "message": "Data product updated."})

        return Response(
            {"success": False, "errors": input_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(
        self,
        request,
        observation_record_pk,
        dragons_run_pk,
        dragons_run_data_product_pk,
        *args,
        **kwargs,
    ):
        # Fetch the linked DRAGONSRunDataProduct entries.
        dragons_run_data_product = get_object_or_404(
            DRAGONSRunDataProduct, pk=dragons_run_data_product_pk
        )

        # Serialize the data.
        serializer = DRAGONSRunDataProductSerializer(dragons_run_data_product)

        return Response(serializer.data)


class DRAGONSRunDataProductSerializer(serializers.ModelSerializer):
    """Serializer for DRAGONSRunDataProduct instances.

    Attributes
    ----------
    product_id : `serializers.CharField`
        The unique identifier of the data product.
    observation_id : `serializers.CharField`
        The observation ID associated with the data product.
    file_type : `serializers.CharField`
        The type of file, e.g., BIAS, DARK, FLAT.
    group_id : `serializers.CharField`
        An optional group ID for grouping related data products.
    exposure_time : `serializers.FloatField`
        The exposure time of the data product.
    object_name : `serializers.CharField`
        The name of the observed object.
    central_wavelength : `serializers.FloatField`
        The central wavelength of the observation.
    wavelength_band : `serializers.CharField`
        The wavelength band of the observation.
    observation_date : `serializers.DateField`
        The date when the observation was made.
    roi_setting : `serializers.CharField`
        The region of interest setting of the detector.
    enabled : `serializers.BooleanField`
        Indicates whether the data product is enabled for processing in a DRAGONS run.

    Notes
    -----
    This serializer dynamically maps `DataProduct` and `DataProductMetadata`
    fields to a flattened structure.
    """

    product_id = serializers.CharField(source="data_product.product_id")
    observation_id = serializers.CharField(
        source="data_product.observation_record.observation_id"
    )
    file_type = serializers.CharField(source="data_product.metadata.file_type")
    group_id = serializers.CharField(
        source="data_product.metadata.group_id", allow_null=True
    )
    exposure_time = serializers.FloatField(
        source="data_product.metadata.exposure_time", allow_null=True
    )
    object_name = serializers.CharField(
        source="data_product.metadata.object_name", allow_null=True
    )
    central_wavelength = serializers.FloatField(
        source="data_product.metadata.central_wavelength", allow_null=True
    )
    wavelength_band = serializers.CharField(
        source="data_product.metadata.wavelength_band", allow_null=True
    )
    observation_date = serializers.DateField(
        source="data_product.metadata.observation_date", allow_null=True
    )
    roi_setting = serializers.CharField(
        source="data_product.metadata.roi_setting", allow_null=True
    )
    enabled = serializers.BooleanField()

    class Meta:
        model = DRAGONSRunDataProduct
        fields = [
            "product_id",
            "observation_id",
            "file_type",
            "group_id",
            "exposure_time",
            "object_name",
            "central_wavelength",
            "wavelength_band",
            "observation_date",
            "roi_setting",
            "enabled",
        ]
