__all__ = ["ProgramKey", "validate_program_id"]

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from goats_tom.ocs import GeminiID

from .key import Key


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


class ProgramKey(Key):
    """Key that allows access to a specific program, requiring a
    program-specific password.
    """

    program_id = models.CharField(max_length=100, validators=[validate_program_id])

    def __str__(self) -> str:
        return f"Key for Program {self.program_id} for User {self.user.username}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Saves the instance after ensuring uniqueness of program_id and
        site.
        """
        # Check if a key with the same program_id and site already exists.
        existing_key = ProgramKey.objects.filter(
            program_id=self.program_id, site=self.site,
        )
        if existing_key.exists():
            # Delete the existing key
            existing_key.delete()

        super().save(*args, **kwargs)
