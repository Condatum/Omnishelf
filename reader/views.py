from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import DetailView

from library.models import LibraryEntry


class ViewportReaderView(LoginRequiredMixin, DetailView):
    """Deep-Link Resume reader launching the active chapter URI inside a sandboxed viewport."""

    model = LibraryEntry
    template_name = 'reader/viewport.html'
    context_object_name = 'entry'
    pk_url_kwarg = 'entry_id'

    def get_queryset(self):
        return (
            LibraryEntry.objects.filter(user=self.request.user)
            .select_related('folder')
            .prefetch_related('tags', 'snapshots')
        )

    def get_object(self, queryset=None):
        entry = super().get_object(queryset=queryset)
        entry.last_read_at = timezone.now()
        entry.save(update_fields=['last_read_at', 'updated_at'])
        return entry
