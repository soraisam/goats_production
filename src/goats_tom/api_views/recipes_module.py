"""API views for recipes module."""

__all__ = ["RecipesModuleViewSet"]

from rest_framework import viewsets

from goats_tom.models import RecipesModule
from goats_tom.serializers import RecipesModuleSerializer


class RecipesModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset that provides read-only access to `RecipesModule` instances.

    Attributes
    ----------
    queryset : `QuerySet`
        The queryset that includes all `RecipesModule` instances from the database.
    serializer_class : `RecipesModuleSerializer`
        The serializer class used to convert `RecipesModule` instances into JSON format.

    """

    queryset = RecipesModule.objects.all()
    serializer_class = RecipesModuleSerializer
