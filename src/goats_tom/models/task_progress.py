__all__ = ["TaskProgress"]

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class TaskProgress(models.Model):
    task_id = models.CharField(max_length=255)
    progress = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(max_length=50, default="running")
    done = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Task {self.task_id} ({self.status})"

    def finish(self, error_message: str | None = None) -> None:
        """Update the end time of the task and optionally record an error
        message.

        Parameters
        ----------
        error_message : `str`, optional
            An error message if the task failed. Default is `None`.
        """
        self.end_time = timezone.now()
        if error_message:
            self.status = "failed"
            self.error_message = error_message
        else:
            self.status = "completed"
        self.progress = 100
        self.save()

    def finalize(self) -> None:
        """Sets 'done' to `True`."""
        self.done = True

    @property
    def total_time(self) -> str:
        """
        Calculate and return the total time taken for the task in a
        human-readable format.

        Returns
        -------
        `str`
            The total time taken for the task formatted as "Wd Xh Ym Zs" or
            "N/A" if not available.
        """
        if self.end_time and self.start_time and self.done:
            duration = self.end_time - self.start_time
            seconds = duration.total_seconds()

            # Calculate days, hours, minutes, and seconds.
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            minutes = int((seconds % 3600) // 60)
            seconds = int(seconds % 60)

            time_parts = []
            if days > 0:
                time_parts.append(f"{days}d")
            if hours > 0:
                time_parts.append(f"{hours}h")
            if minutes > 0:
                time_parts.append(f"{minutes}m")
            if seconds > 0 or not time_parts:
                time_parts.append(f"{seconds}s")

            return " ".join(time_parts)
        return "N/A"
