import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ReadingStatus(models.TextChoices):
    """Multi-tier reading status taxonomy for serialized literature."""

    ACTIVE = 'ACTIVE', 'Active Reading'
    ON_HOLD = 'ON_HOLD', 'On Hold'
    BINGE_READY = 'BINGE_READY', 'Binge-Ready'
    HIATUS = 'HIATUS', 'Hiatus'
    COMPLETED = 'COMPLETED', 'Completed'


class Folder(models.Model):
    """User-scoped folder for grouping serialized stories."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='folders',
    )
    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=32, blank=True, default='folder')
    color_hex = models.CharField(max_length=7, default='#6366f1')
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_folder_name_per_user',
            )
        ]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """User-scoped flexible tag for cross-cutting genre/trope/platform labels."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags',
    )
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, blank=True)
    color_hex = models.CharField(max_length=7, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'slug'],
                name='unique_tag_slug_per_user',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
