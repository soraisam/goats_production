__all__ = ["UserKey"]

from django.db import models

from .key import Key


class UserKey(Key):
    """Key associated with a user, granting access to all programs linked to
    the email.
    """

    email = models.EmailField()
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Key for User {self.user.username}"

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
