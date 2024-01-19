from typing import Any

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .gemini_id import GeminiID


class GOALogin(models.Model):
    """GOALogin Model

    Model that keeps track of GOA login information for each user.

    Attributes
    ----------
    user : `models.OneToOneField`
        The user to which the GOA login belongs.
    username : `models.CharField`
        The GOA login username.
    password : `models.CharField`
        The GOA login password, stored as a securely hashed value.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="goa_login"
    )
    username = models.CharField(max_length=100)
    # Making this 128 to store encrypted passwords.
    password = models.CharField(max_length=128)

    def clean(self) -> None:
        """Custom validation.

        Exceptions
        ----------
        ValidatorError
            Raised if 'username' is empty.
        ValidationError
            Raised if 'password' is empty.
        """
        if not self.username.strip():
            raise ValidationError("Username cannot be empty")

        if not self.password.strip():
            raise ValidationError("Password cannot be empty")

    def set_password(self, raw_password: str) -> None:
        """Sets the user's password to the given raw string, taking care of the
        password hashing.

        Parameters
        ----------
        raw_password : `str`
            The plaintext password to set, which will be hashed before storage.
        """
        self.password = make_password(raw_password)

    class Meta:
        verbose_name = "GOA Login"
        verbose_name_plural = "GOA Logins"


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


def validate_program_id(value: str) -> None:
    """Validates that the provided value is a valid program ID.

    Parameters
    ----------
    value : `str`
        The program ID to validate.

    Raises
    ------
    ValidationError
        Raised if the program ID is not valid.
    """
    if not GeminiID.is_valid_program_id(value):
        raise ValidationError(f"{value} is not a valid Gemini program ID.")


class Key(models.Model):
    """Abstract base class for representing a key, either a user or program
    key.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    site = models.CharField(
        max_length=2, choices=[("GS", "Gemini South"), ("GN", "Gemini North")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def activate(self) -> None:
        """Activates this key, ensuring that no other keys for the same entity
        are active.
        """
        # TODO: Want to allow active keys for both sites?
        type(self).objects.filter(user=self.user, site=self.site).update(
            is_active=False
        )
        self.is_active = True
        self.save()

    def deactivate(self) -> None:
        """Deactivates this key."""
        self.is_active = False
        self.save()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Saves the instance."""
        self.password = make_password(self.password)
        super().save(*args, **kwargs)


class UserKey(Key):
    """Key associated with a user, granting access to all programs linked to
    the email.
    """

    email = models.EmailField()

    def __str__(self) -> str:
        return f"Key for User {self.user.username}"


class ProgramKey(Key):
    """Key that allows access to a specific program, requiring a
    program-specific password.
    """

    program_id = models.CharField(max_length=100, validators=[validate_program_id])

    def __str__(self) -> str:
        return f"Key for Program {self.program_id} for User {self.user.username}"
