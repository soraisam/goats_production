"""Model for a recipe in DRAGONS."""

import re

from django.db import models

from .dragons_run import DRAGONSRun


class DRAGONSRecipe(models.Model):
    dragons_run = models.ForeignKey(
        DRAGONSRun, on_delete=models.CASCADE, related_name="recipes"
    )
    file_type = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("dragons_run", "file_type", "name")

    def __str__(self) -> str:
        return f"{self.file_type} - {self.name}"

    @property
    def short_name(self) -> str | None:
        """Extracts the short name from the recipe's full name.

        Returns
        -------
        `str | None`
            The short name extracted after "::" if present.
        """
        # Regular expression pattern to capture text after "::".
        pattern = r"::(\w+)$"
        # Using re.search to find the match.
        match = re.search(pattern, self.name)
        if match:
            return match.group(1)
        return None
