import uuid
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.utils import timezone
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


class LibraryEntry(models.Model):
    """Stateful URI pointer and metadata override record for serialized literature."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='library_entries',
    )
    custom_title = models.CharField(max_length=255)
    original_source_title = models.CharField(max_length=255, blank=True)
    custom_cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    custom_cover_url = models.URLField(max_length=2000, blank=True)
    current_uri = models.URLField(max_length=2000)
    source_domain = models.CharField(max_length=255, blank=True)
    chapter_label = models.CharField(max_length=120, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ReadingStatus.choices,
        default=ReadingStatus.ACTIVE,
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entries',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='entries')
    notes = models.TextField(blank=True)
    last_read_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_read_at', 'custom_title']

    def save(self, *args, **kwargs):
        if self.current_uri:
            netloc = urlparse(self.current_uri).netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            self.source_domain = netloc
        super().save(*args, **kwargs)

    @property
    def cover_src(self) -> str:
        """Return the highest-priority cover image URL (uploaded file > external URL)."""
        if self.custom_cover_image:
            try:
                return self.custom_cover_image.url
            except ValueError:
                pass
        return self.custom_cover_url or ''

    @property
    def fallback_gradient(self) -> str:
        """Return a deterministic dark-mode gradient class for stories without cover art."""
        gradients = (
            'from-indigo-950 via-slate-900 to-violet-950',
            'from-slate-900 via-cyan-950 to-indigo-950',
            'from-emerald-950 via-slate-900 to-teal-950',
            'from-rose-950 via-slate-900 to-indigo-950',
            'from-amber-950 via-slate-900 to-stone-900',
            'from-fuchsia-950 via-slate-900 to-indigo-950',
        )
        seed = sum(ord(ch) for ch in (self.custom_title or 'OmniShelf'))
        return gradients[seed % len(gradients)]

    @property
    def status_badge_classes(self) -> str:
        """Return high-contrast badge styling classes matching ReadingStatus."""
        styles = {
            ReadingStatus.ACTIVE: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
            ReadingStatus.BINGE_READY: 'bg-indigo-500/20 text-indigo-200 ring-indigo-400/40',
            ReadingStatus.ON_HOLD: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
            ReadingStatus.HIATUS: 'bg-rose-500/15 text-rose-300 ring-rose-500/30',
            ReadingStatus.COMPLETED: 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
        }
        return styles.get(self.status, 'bg-slate-700/60 text-slate-200 ring-slate-500/30')

    def __str__(self) -> str:
        return f'{self.custom_title} ({self.chapter_label or "No chapter"})'



class ReadingSnapshot(models.Model):
    """Immutable audit trail of frozen chapter URIs for a LibraryEntry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry = models.ForeignKey(
        LibraryEntry,
        on_delete=models.CASCADE,
        related_name='snapshots',
    )
    uri = models.URLField(max_length=2000)
    chapter_label = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.entry.custom_title} @ {self.chapter_label or self.uri}'
