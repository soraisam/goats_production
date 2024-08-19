"""Module that handles the DRAGONS files API."""

from collections import defaultdict

from django.db.models import CharField, F, QuerySet, Value
from django.db.models.fields.json import KeyTransform
from django.db.models.functions import Concat
from django.http import HttpRequest
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from goats_tom.filters import AstrodataFilter
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
        filter_serializer.is_valid(raise_exception=True)

        dragons_run_pk = filter_serializer.validated_data.get("dragons_run")
        file_type = filter_serializer.validated_data.get("file_type")
        object_name = filter_serializer.validated_data.get("object_name")

        if dragons_run_pk is not None:
            queryset = queryset.filter(dragons_run__pk=dragons_run_pk)

        if file_type is not None:
            queryset = queryset.filter(file_type=file_type)
            if file_type == "object":
                queryset = queryset.filter(object_name=object_name)

        # Apply select_related to optimize related object retrieval.
        queryset = queryset.select_related(
            "data_product__observation_record",
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
        filter_serializer.is_valid(raise_exception=True)

        # Extract validated data.
        group_by_file_type = filter_serializer.validated_data.get("group_by_file_type")
        group_by = filter_serializer.validated_data.get("group_by", [])
        filter_expression = filter_serializer.validated_data.get(
            "filter_expression", ""
        )
        filter_strict = filter_serializer.validated_data.get("filter_strict", False)

        astrodata_filter = AstrodataFilter(strict=filter_strict)
        query_filter = astrodata_filter.parse_expression_to_query(filter_expression)

        # Gets the query.
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(query_filter)

        if group_by:
            annotations = {
                f"group_value_{i}": KeyTransform(key, "astrodata_descriptors")
                for i, key in enumerate(group_by)
            }
            queryset = queryset.annotate(**annotations)

            concat_args = []
            for i, _ in enumerate(group_by):
                if i > 0:
                    concat_args.append(Value(" | "))
                concat_args.append(F(f"group_value_{i}"))

            if len(concat_args) > 1:
                queryset = queryset.annotate(
                    composite_group_value=Concat(*concat_args, output_field=CharField())
                )
                group_field = "composite_group_value"
            else:
                group_field = "group_value_0"

            # Fetch and group data based on the composite or single group key.
            queryset = queryset.values(
                "id",
                "enabled",
                "object_name",
                "file_type",
                "product_id",
                "url",
                group_field,
            ).order_by(group_field)

            # Manually aggregate grouped data.
            grouped_data = {}
            for item in queryset:
                group_key = item[group_field]
                if group_key not in grouped_data:
                    grouped_data[group_key] = {
                        "count": 0,  # Initialize count
                        "files": [],
                    }
                grouped_data[group_key]["files"].append(
                    {
                        "id": item["id"],
                        "enabled": item["enabled"],
                        "object_name": item["object_name"],
                        "file_type": item["file_type"],
                        "product_id": item["product_id"],
                        "url": item["url"],
                    }
                )
                grouped_data[group_key]["count"] += 1

            return Response(grouped_data)

        if group_by_file_type:
            # Don't worry about pagination and group by file type.
            serializer = self.get_serializer(queryset, many=True)
            grouped_data = defaultdict(list)
            for item in serializer.data:
                grouped_data[(item["file_type"]).lower()].append(item)

            if "object" in grouped_data:
                object_group = defaultdict(list)
                for obj_item in grouped_data["object"]:
                    sub_type = obj_item.get("object_name", "")
                    object_group[sub_type].append(obj_item)
                grouped_data["object"] = dict(
                    object_group
                )  # Replace the list with a dictionary of sub_types

            data = dict(grouped_data)
            return Response({"results": data})

        # Paginate and return data.
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
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
        request : `HttpRequest`
            The HTTP request object, containing query parameters.

        Returns
        -------
        `Response`
            Contains serialized DRAGONS file data with optional information.

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

            if "groups" in include:
                data["groups"] = instance.list_groups()

        return Response(data)
