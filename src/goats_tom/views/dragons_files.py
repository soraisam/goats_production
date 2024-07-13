"""Module that handles the DRAGONS files API."""

from collections import defaultdict

from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from goats_tom.models import DRAGONSFile
from goats_tom.serializers import (
    DRAGONSFileFilterSerializer,
    DRAGONSFileSerializer,
)
from goats_tom.utils import get_astrodata_header


class DRAGONSFilesViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """A viewset that provides `retrieve`, `list`, and `update` actions for
    DRAGONS files.
    """

    serializer_class = DRAGONSFileSerializer
    filter_serializer_class = DRAGONSFileFilterSerializer
    permission_classes = [IsAuthenticated]
    queryset = DRAGONSFile.objects.all()

    def get_queryset(self) -> QuerySet:
        """Retrieves the queryset filtered by the associated DRAGONS run.

        Returns
        -------
        `QuerySet`
            The filtered queryset.

        """
        queryset = super().get_queryset()

        # run query parameters through the serializer.
        filter_serializer = self.filter_serializer_class(data=self.request.query_params)

        # Check if any filters provided.
        filter_serializer.is_valid(raise_exception=False)

        dragons_run_pk = filter_serializer.validated_data.get("dragons_run")

        if dragons_run_pk is not None:
            queryset = queryset.filter(dragons_run__pk=dragons_run_pk)

        # Apply select_related to optimize related object retrieval.
        queryset = queryset.select_related(
            "data_product__observation_record", "data_product__metadata",
        )

        return queryset

    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        """List or group DRAGONS file records based on the provided query parameters.

        Parameters
        ----------
        request : `HttpRequest`
            The HTTP request object, containing query parameters.

        Returns
        -------
        `Response`
            The paginated list of DRAGONS file records, optionally grouped by file type.

        """
        # Validates the provided query parameters.
        filter_serializer = self.filter_serializer_class(data=request.query_params)
        filter_serializer.is_valid(raise_exception=False)
        group_by_file_type = filter_serializer.validated_data.get("group_by_file_type")

        # Gets the query.
        queryset = self.filter_queryset(self.get_queryset())

        if group_by_file_type:
            # Don't worry about pagination and group by file type.
            serializer = self.get_serializer(queryset, many=True)
            grouped_data = defaultdict(list)
            for item in serializer.data:
                grouped_data[(item["file_type"]).lower()].append(item)
            data = dict(grouped_data)
            return Response({"results": data})

        # Paginate and return data.
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset, many=True,
        )

        data = serializer.data
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Retrieve a DRAGONS file instance along with optional included data based on
        query parameters.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object, containing query parameters.

        Returns
        -------
        `Response`
            Contains serialized DRAGONS file data with optional header information.

        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Validate the query parameters.
        filter_serializer = self.filter_serializer_class(data=request.query_params)
        # If valid, attach the additional information.
        if filter_serializer.is_valid(raise_exception=False):
            include = filter_serializer.validated_data.get("include", [])

            if "header" in include:
                header = get_astrodata_header(instance.data_product)
                data["header"] = header

        return Response(data)
