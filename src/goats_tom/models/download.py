__all__ = ["Download"]


from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Download(models.Model):
    unique_id = models.CharField(max_length=255)
    observation_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Running")
    done = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    num_files_downloaded = models.IntegerField(blank=True, null=True)
    num_files_omitted = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Download {self.observation_id}: ({self.status})"

    def finish(self, message: str | None = None, error: bool = False) -> None:
        """Update the end time of the download and optionally record an error
        message.

        Parameters
        ----------
        message : `str`, optional
            A message about the download, by default `None`.

        """
        self.end_time = timezone.now()
        if error:
            self.error = error
            self.status = "Failed"
        else:
            self.status = "Completed"
        self.message = message
        self.done = True
        self.save()

    @property
    def total_time(self) -> str:
        """Calculate and return the total time taken for the download in a
        human-readable format.

        Returns
        -------
        `str`
            The total time taken for the download formatted as "Wd Xh Ym Zs" or
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
