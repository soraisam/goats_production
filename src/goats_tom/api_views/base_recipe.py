"""Views for base recipes."""

__all__ = ["BaseRecipeViewSet"]

from rest_framework import viewsets

from goats_tom.models import BaseRecipe
from goats_tom.serializers import BaseRecipeSerializer


class BaseRecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset that provides read-only access to `BaseRecipe` instances.

    Attributes
    ----------
    queryset : `QuerySet`
        The queryset that includes all `BaseRecipe` instances from the database.
    serializer_class : `BaseRecipeSerializer`
        The serializer class used to convert `BaseRecipe` instances into JSON format.

    """

    queryset = BaseRecipe.objects.all()
    serializer_class = BaseRecipeSerializer
