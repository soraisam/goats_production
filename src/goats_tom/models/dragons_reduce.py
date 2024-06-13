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
        "starting", "running", "done", or "error". The default status at creation is
        "starting".
    """

    STATUS_CHOICES = [
        ("created", "Created"),
        ("queued", "Queued"),
        ("initializing", "Initializing"),
        ("running", "Running"),
        ("done", "Done"),
        ("error", "Error"),
    ]

    recipe = models.ForeignKey(
        DRAGONSRecipe, on_delete=models.CASCADE, related_name="reductions"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, default="created")

    def __str__(self):
        return f"Reduction {self.id} - {self.recipe.name}"

    def mark_queued(self) -> None:
        """Marks the reduction as queued."""
        self.status = "queued"
        self.save()

    def mark_initializing(self) -> None:
        """Marks the reduction as initializing."""
        self.status = "initializing"
        self.save()

    def mark_done(self) -> None:
        """Marks the reduction as completed and records the completion time."""
        self.status = "done"
        self.end_time = timezone.now()
        self.save()

    def mark_error(self) -> None:
        """Marks the reduction as an error and records the error time."""
        self.status = "error"
        self.end_time = timezone.now()
        self.save()

    def mark_running(self) -> None:
        """Marks the reduction status as running."""
        self.status = "running"
        self.save()
