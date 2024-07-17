__all__ = ["Key"]

from django.contrib.auth.models import User
from django.db import models
from django_cryptography.fields import encrypt


class Key(models.Model):
    """Abstract base class for representing a key, either a user or program
    key.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = encrypt(models.CharField(max_length=100))
    site = models.CharField(
        max_length=2, choices=[("GS", "Gemini South"), ("GN", "Gemini North")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
