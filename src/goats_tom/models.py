# Standard library imports.

# Related third party imports.
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models

# Local application/library specific imports.


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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='goa_login')
    username = models.CharField(max_length=100)
    # Making this 128 to store encrypted passwords.
    password = models.CharField(max_length=128)

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
