"""Model for a recipe in DRAGONS."""

__all__ = ["BaseRecipe"]

import re

from django.db import models


class BaseRecipe(models.Model):
    """Represents a base recipe in the DRAGONS system, storing essential
    attributes of a data reduction recipe.

    Attributes
    ----------
    name : `models.CharField`
        The name of the recipe.
    function_definition : `models.TextField`
        The textual representation of the recipe's function.
    is_default : `models.BooleanField`
        Flag indicating if this recipe is the default for its file type and version.
    recipes_module : `models.ForeignKey`
        An optional foreign key to the `RecipesModule`, indicating which
        recipes module is associated with this recipe.

    """

    name = models.CharField(max_length=255, editable=False, blank=False, null=False)
    function_definition = models.TextField(editable=False, blank=False, null=False)
    is_default = models.BooleanField(
        editable=False,
        null=False,
        blank=False,
        default=False,
    )
    recipes_module = models.ForeignKey(
        "goats_tom.RecipesModule", on_delete=models.CASCADE, related_name="base_recipes"
    )

    class Meta:
        unique_together = ("name", "recipes_module")

    def __str__(self) -> str:
        return f"Base recipe {self.name} for {self.recipes_module}"

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

    @property
    def version(self) -> str:
        """Provides the version derived from the linked recipes module.

        Returns
        -------
        `str`
            The version from the recipes module.

        """
        return self.recipes_module.version

    @property
    def instrument(self) -> str:
        """Provides the instrument derived from the linked recipes module.

        Returns
        -------
        `str`
            The instrument from the recipes module.

        """
        return self.recipes_module.instrument

    @property
    def recipes_module_name(self) -> str:
        """Provides the recipes module name.

        Returns
        -------
        `str`
            The recipes module name.

        """
        return self.recipes_module.name
