"""Views for DRAGONS operations."""

__all__ = [
    "DRAGONSSetupAPIView",
    "DRAGONSView",
]

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from goats_tom.serializers import DRAGONSRunSerializer
from recipe_system import cal_service
from rest_framework import status
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

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
