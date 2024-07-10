"""Model for a recipe in DRAGONS."""

import re
from typing import Any

from django.db import models

from .dragons_run import DRAGONSRun


class DRAGONSRecipe(models.Model):
    dragons_run = models.ForeignKey(
        DRAGONSRun,
        on_delete=models.CASCADE,
        related_name="recipes",
        editable=False,
        blank=False,
        null=False,
    )
    file_type = models.CharField(
        max_length=100, editable=False, blank=False, null=False
    )
    name = models.CharField(max_length=255, editable=False, blank=False, null=False)
    original_function_definition = models.TextField(
        editable=False, blank=False, null=False
    )
    function_definition = models.TextField(
        blank=True, null=True, help_text="Revised function definition by the user."
    )

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

    @property
    def active_function_definition(self) -> str:
        """Returns the currently active function definition, either modified or original.

        Returns
        -------
        `str`
            Returns the original function definition unless modified exists.
        """
        return self.function_definition or self.original_function_definition

    def reset_to_original(self, save: bool = True) -> None:
        """Resets the modified function to the original.

        Parameters
        ----------
        save : `bool`
            If `True`, saves the instance.
        """
        self.function_definition = None
        if save:
            self.save()

    def list_primitives_and_docstrings(self) -> dict[str, Any]:
        """Retrieves the first file matching a specific file type from a collection
        managed by a DRAGONS run, and lists all available primitives and their
        documentation associated with that file.

        Returns
        -------
        `dict[str, Any]`
            A dictionary containing the method names as keys and their associated
            parameters and docstrings if a matching file is found. Returns an empty
            dictionary if no matching file is found.
        """
        first_file = self.dragons_run.dragons_run_files.filter(
            data_product__metadata__file_type=self.file_type
        ).first()

        if first_file:
            return first_file.list_primitives_and_docstrings()
        
        return {}
