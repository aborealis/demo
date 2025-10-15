"""Database table structure for organization and member profiles"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Entity(models.Model):
    """Organization (entity) model"""
    name = models.CharField(max_length=200)
    website = models.CharField(max_length=200)
    image = models.ImageField(upload_to="static/img/logo/", blank=True)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name_plural = "My Organization"


class User(AbstractUser):
    """Override the uniqueness property of the built-in field"""
    email = models.EmailField(unique=True)
    entity = models.ForeignKey(
        Entity, on_delete=models.DO_NOTHING,
        null=True,
        default=None
    )

    def __str__(self) -> str:
        return f'{self.last_name} {self.first_name}'

    class Meta:
        ordering = ['last_name', 'first_name']
