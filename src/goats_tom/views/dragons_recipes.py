"""Module that handles the DRAGONS recipe API."""

from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from goats_tom.models import DRAGONSRecipe
from goats_tom.serializers import DRAGONSRecipeFilterSerializer, DRAGONSRecipeSerializer


class DRAGONSRecipesViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = DRAGONSRecipe.objects.all()
    serializer_class = DRAGONSRecipeSerializer
    filter_serializer_class = DRAGONSRecipeFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """Retrieves the queryset based on the filter provided in query parameters.

        Returns
        -------
        `QuerySet`
            A `QuerySet` of `DRAGONSRecipe` filtered by the provided parameters.
        """
        queryset = super().get_queryset()

        # Run query parameters through the serializer.
        filter_serializer = self.filter_serializer_class(data=self.request.query_params)

        # Check if any filters provided.
        if filter_serializer.is_valid(raise_exception=False):
            dragons_run_pk = filter_serializer.validated_data.get("dragons_run")
            file_type = filter_serializer.validated_data.get("file_type")
            if dragons_run_pk is not None:
                queryset = queryset.filter(dragons_run__pk=dragons_run_pk)
            if file_type is not None:
                queryset = queryset.filter(file_type=file_type)

        return queryset

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Retrieves a serialized representation of an object from a Django model,
        possibly including additional information based on query parameters.

        Parameters
        ----------
        request : `HttpRequest`
            The HTTP request object that may include query parameters.

        Returns
        -------
        `Response`
            Response object containing the serialized data of the requested object. If
            specified in the query parameters, additional data is included.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Validate the query parameters.
        filter_serializer = self.filter_serializer_class(data=request.query_params)
        # If valid, attach the additional information.
        if filter_serializer.is_valid(raise_exception=False):
            include = filter_serializer.validated_data.get("include", [])

            if "help" in include:
                data["help"] = instance.list_primitives_and_docstrings()

        return Response(data)
