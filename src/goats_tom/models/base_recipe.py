"""Model for a recipe in DRAGONS."""

__all__ = ["BaseRecipe"]

import re

from django.db import models


class BaseRecipe(models.Model):
    """Represents a base recipe in the DRAGONS system, storing essential
    attributes of a data reduction recipe.

    Attributes
    ----------
    file_type : `models.CharField`
        The type of file the recipe is associated with.
    name : `models.CharField`
        The name of the recipe.
    function_definition : `models.TextField`
        The textual representation of the recipe's function.
    version : `models.CharField`
        The version of the DRAGONS system the recipe is compatible with.
    is_default : `models.BooleanField`
        Flag indicating if this recipe is the default for its file type and version.

    """

    file_type = models.CharField(
        max_length=100, editable=False, blank=False, null=False,
    )
    name = models.CharField(max_length=255, editable=False, blank=False, null=False)
    function_definition = models.TextField(editable=False, blank=False, null=False)
    version = models.CharField(
        max_length=30,
        editable=False,
        blank=False,
        null=False,
    )
    is_default = models.BooleanField(
        editable=False, null=False, blank=False, default=False,
    )

    class Meta:
        unique_together = ("file_type", "name", "version")

    def __str__(self) -> str:
        return f"v{self.version} {self.name}"

    @property
    def short_name(self) -> str:
        """Extracts the short name from the recipe's full name.

        Returns
        -------
        `str`
            The short name extracted after "::" if present.

        """
        # Regular expression pattern to capture text after "::".
        pattern = r"::(\w+)$"
        # Using re.search to find the match.
        match = re.search(pattern, self.name)
        if match:
            return match.group(1)
        return "Unknown"
