__all__ = ["GOALogin"]

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django_cryptography.fields import encrypt


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
    password = encrypt(models.CharField(max_length=128))

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

    class Meta:
        verbose_name = "GOA Login"
        verbose_name_plural = "GOA Logins"
