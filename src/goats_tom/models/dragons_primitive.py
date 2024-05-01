"""Model for DRAGONS recipe primitives."""

from django.db import models

from .dragons_recipe import DRAGONSRecipe


class DRAGONSPrimitive(models.Model):
    recipe = models.ForeignKey(
        DRAGONSRecipe, on_delete=models.CASCADE, related_name="primitives"
    )
    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.recipe.name} - {self.name}: {'Enabled' if self.enabled else 'Disabled'}"
