"""Module for DRAGONS reduction."""

__all__ = ["DRAGONSReduce"]
from django.db import models
from django.utils import timezone

from goats_tom.models import DRAGONSRecipe


class DRAGONSReduce(models.Model):
    """Represents a reduction process associated with a specific recipe in the DRAGONS
    system.

    Attributes
    ----------
    recipe : `models.ForeignKey`
        A reference to the `DRAGONSRecipe` model, establishing a many-to-one
        relationship where each reduction is linked to a specific recipe.
    start_time : `models.DateTimeField`
        The timestamp indicating when the reduction process was initiated. This field
        is automatically set to the current time when the reduction object is created.
    end_time : `models.DateTimeField`
        The timestamp indicating when the reduction process was completed or terminated
        with an error. This field is optional and is set only when the reduction ends.
    status : `models.CharField`
        The current status of the reduction process. It can be one of the following:
        "created", "starting", "running", "canceled", "done", or "error". The default
        status at creation is "created".
    """

    STATUS_CHOICES = [
        ("created", "Created"),
        ("queued", "Queued"),
        ("initializing", "Initializing"),
        ("running", "Running"),
        ("done", "Done"),
        ("error", "Error"),
        ("canceled", "Canceled"),
    ]

    recipe = models.ForeignKey(
        DRAGONSRecipe,
        on_delete=models.CASCADE,
        related_name="reductions",
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    start_time = models.DateTimeField(null=True, blank=True, editable=False)
    end_time = models.DateTimeField(null=True, blank=True, editable=False)
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, default="created")
    task_id = models.CharField(max_length=255, null=True, blank=True, editable=False)

    def __str__(self):
        return f"Reduction {self.id} - {self.recipe.name}"

    def mark_queued(self, save: bool = True) -> None:
        """Marks the reduction as queued.

        Parameters
        ----------
        save : `bool`
            Saves to the database, default is `True`.
        """
        self.status = "queued"
        if save:
            self.save()

    def mark_initializing(self, save: bool = True) -> None:
        """Marks the reduction as initializing.

        Parameters
        ----------
        save : `bool`
            Saves to the database, default is `True`.
        """
        self.status = "initializing"
        self.start_time = timezone.now()
        if save:
            self.save()

    def mark_done(self, save: bool = True) -> None:
        """Marks the reduction as completed and records the completion time.

        Parameters
        ----------
        save : `bool`
            Saves to the database, default is `True`.
        """
        self.status = "done"
        self.end_time = timezone.now()
        if save:
            self.save()

    def mark_error(self, save: bool = True) -> None:
        """Marks the reduction as an error and records the error time.

        Parameters
        ----------
        save : `bool`
            Saves to the database, default is `True`.
        """
        self.status = "error"
        self.end_time = timezone.now()
        if save:
            self.save()

    def mark_running(self, save: bool = True) -> None:
        """Marks the reduction status as running.

        Parameters
        ----------
        save : `bool`
            Saves to the database, default is `True`.
        """
        self.status = "running"
        if save:
            self.save()

    def mark_canceled(self, save: bool = True) -> None:
        """Marks the reduction status as canceled.

        Parameters
        ----------
        save : `bool`
            Saves to the database, default is `True`.
        """
        self.status = "canceled"
        self.end_time = timezone.now()
        if save:
            self.save()

    def get_label(self) -> str:
        """Generates the label for the reduce notification.

        Returns
        -------
        `str`
            The generated label.
        """
        return f"{self.recipe.dragons_run}::{self.recipe.short_name}"
