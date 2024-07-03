"""Module that handles the DRAGONS recipe API."""

from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

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
