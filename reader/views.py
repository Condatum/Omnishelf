import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from library.models import LibraryEntry, ReadingSnapshot

from .forms import FreezeSnapshotForm
from .utils import increment_chapter_label


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['snapshots'] = self.object.snapshots.all()
        context['next_chapter_preview'] = increment_chapter_label(self.object.chapter_label)
        return context


def _render_hud_snapshot_response(request, entry: LibraryEntry, confirmation_text: str) -> HttpResponse:
    """Return HUD confirmation badge plus OOB updates for badges, history drawer, and fallback link."""
    snapshots = entry.snapshots.all()
    badge_html = render_to_string(
        'reader/partials/freeze_confirmation.html',
        {'confirmation_text': confirmation_text, 'entry': entry},
        request=request,
    )
    hud_meta_html = render_to_string(
        'reader/partials/hud_oob_updates.html',
        {'entry': entry, 'snapshots': snapshots},
        request=request,
    )
    response = HttpResponse(badge_html + hud_meta_html)
    response['HX-Trigger'] = json.dumps({
        'snapshotFrozen': {
            'uri': entry.current_uri,
            'chapter_label': entry.chapter_label,
            'source_domain': entry.source_domain,
            'notes': entry.notes,
        },
        'show-toast': {'message': confirmation_text, 'level': 'success'},
    })
    return response


@login_required
def quick_snapshot_modal_view(request, entry_id):
    """Render the quick Freeze Snapshot modal triggered from a Grand Library card."""
    entry = get_object_or_404(LibraryEntry, pk=entry_id, user=request.user)
    context = {
        'entry': entry,
        'next_chapter_preview': increment_chapter_label(entry.chapter_label),
    }
    if request.htmx:
        return render(request, 'reader/partials/quick_snapshot_modal.html', context)
    return redirect('reader:viewport', entry_id=entry.pk)


@login_required
@require_POST
def freeze_snapshot_view(request, entry_id):
    """Freeze a new chapter URI snapshot, update LibraryEntry, and log immutable ReadingSnapshot."""
    entry = get_object_or_404(LibraryEntry, pk=entry_id, user=request.user)
    form = FreezeSnapshotForm(request.POST)

    if not form.is_valid():
        error_msg = next(iter(form.errors.values()))[0]
        if request.htmx:
            html = render_to_string(
                'reader/partials/freeze_confirmation.html',
                {'error_text': f'Could not freeze snapshot: {error_msg}', 'entry': entry},
                request=request,
            )
            return HttpResponse(html)
        messages.error(request, f'Could not freeze snapshot: {error_msg}')
        return redirect('reader:viewport', entry_id=entry.pk)

    uri = form.cleaned_data['uri'].strip()
    chapter_label = (form.cleaned_data['chapter_label'] or '').strip()
    if request.POST.get('increment_chapter') == '1':
        chapter_label = increment_chapter_label(chapter_label or entry.chapter_label)
    notes = form.cleaned_data['notes'].strip() if 'notes' in request.POST else entry.notes

    entry.current_uri = uri
    entry.chapter_label = chapter_label
    entry.notes = notes
    entry.last_read_at = timezone.now()
    entry.save()  # Re-evaluates source_domain automatically via urlparse

    ReadingSnapshot.objects.create(
        entry=entry,
        uri=entry.current_uri,
        chapter_label=entry.chapter_label,
        notes=entry.notes,
    )

    label_display = entry.chapter_label or entry.source_domain or 'current URI'
    confirmation_text = f'Snapshot Frozen at {label_display}'

    if request.htmx:
        if request.POST.get('source') == 'card':
            card_html = render_to_string(
                'library/partials/entry_card.html',
                {'entry': entry},
                request=request,
            )
            response = HttpResponse(card_html)
            response['HX-Trigger'] = json.dumps({
                'closeModal': True,
                'show-toast': {'message': confirmation_text, 'level': 'success'},
            })
            return response
        return _render_hud_snapshot_response(request, entry, confirmation_text)

    messages.success(request, confirmation_text)
    return redirect('reader:viewport', entry_id=entry.pk)


@login_required
@require_POST
def rollback_snapshot_view(request, entry_id, snapshot_id):
    """Roll back a LibraryEntry's active URI & chapter label to a previously frozen ReadingSnapshot."""
    entry = get_object_or_404(LibraryEntry, pk=entry_id, user=request.user)
    snapshot = get_object_or_404(ReadingSnapshot, pk=snapshot_id, entry=entry)

    entry.current_uri = snapshot.uri
    entry.chapter_label = snapshot.chapter_label
    entry.notes = snapshot.notes
    entry.last_read_at = timezone.now()
    entry.save()

    ReadingSnapshot.objects.create(
        entry=entry,
        uri=entry.current_uri,
        chapter_label=entry.chapter_label,
        notes=entry.notes,
    )

    label_display = entry.chapter_label or entry.source_domain or 'previous URI'
    confirmation_text = f'Rolled back to {label_display}'

    if request.htmx:
        return _render_hud_snapshot_response(request, entry, confirmation_text)

    messages.info(request, confirmation_text)
    return redirect('reader:viewport', entry_id=entry.pk)
