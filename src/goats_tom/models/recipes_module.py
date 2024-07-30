"""Module for Recipes modules."""

__all__ = ["RecipesModule"]

from django.db import models


class RecipesModule(models.Model):
    """Represents a module containing data processing recipes for a specific instrument
    and version.

    Attributes
    ----------
    name : `models.CharField`
        The name of the recipes module.
    version : `models.CharField`
        The version of the DRAGONS recipes module..
    instrument : `models.CharField`
        The instrument associated with the recipes module.

    """

    name = models.CharField(
        max_length=100,
        editable=False,
        blank=False,
        null=False,
    )
    version = models.CharField(
        max_length=30,
        editable=False,
        blank=False,
        null=False,
    )
    instrument = models.CharField(
        max_length=50,
        editable=False,
        blank=False,
        null=False,
    )

    class Meta:
        unique_together = ("name", "version", "instrument")

    def __str__(self):
        return f"{self.name} (v{self.version}) for {self.instrument}"
