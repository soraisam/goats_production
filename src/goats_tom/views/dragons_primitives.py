"""Module for API views for DRAGONS primimtives."""

from django.db.models import QuerySet
from rest_framework import viewsets

from goats_tom.models import DRAGONSPrimitive
from goats_tom.serializers import (
    DRAGONSPrimitiveFilterSerializer,
    DRAGONSPrimitiveSerializer,
)


class DRAGONSPrimitivesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DRAGONSPrimitive.objects.all()
    serializer_class = DRAGONSPrimitiveSerializer
    filter_serializer_class = DRAGONSPrimitiveFilterSerializer

    def get_queryset(self) -> QuerySet:
        """Retrieves the queryset based on the filter provided in query parameters.

        Returns
        -------
        `QuerySet`
            A `QuerySet` of `DRAGONSPrimitive` filtered by the provided parameters.
        """
        queryset = super().get_queryset()

        # Run query parameters through the serializer.
        filter_serializer = self.filter_serializer_class(data=self.request.query_params)

        # Check if any filters provided.
        if filter_serializer.is_valid(raise_exception=False):
            recipe_pk = filter_serializer.validated_data.get("recipe")
            if recipe_pk is not None:
                queryset = queryset.filter(recipe__pk=recipe_pk)

        return queryset
