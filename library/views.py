import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import LibraryEntryForm
from .models import Folder, LibraryEntry, ReadingSnapshot, ReadingStatus, Tag


def _get_user_library_context(user):
    """Build strictly user-scoped entries and stats context for Grand Library responses."""
    entries = (
        LibraryEntry.objects.filter(user=user)
        .select_related('folder')
        .prefetch_related('tags')
    )
    stats = LibraryEntry.objects.filter(user=user).aggregate(
        total_count=Count('id'),
        active_count=Count('id', filter=Q(status=ReadingStatus.ACTIVE)),
        binge_ready_count=Count('id', filter=Q(status=ReadingStatus.BINGE_READY)),
        on_hold_count=Count('id', filter=Q(status=ReadingStatus.ON_HOLD)),
        hiatus_count=Count('id', filter=Q(status=ReadingStatus.HIATUS)),
        completed_count=Count('id', filter=Q(status=ReadingStatus.COMPLETED)),
    )
    return {
        'entries': entries,
        **stats,
        'folders': Folder.objects.filter(user=user),
        'tags': Tag.objects.filter(user=user),
        'status_choices': ReadingStatus.choices,
    }


def _render_htmx_grid_response(request, toast_message: str, level: str = 'success') -> HttpResponse:
    """Return updated entry grid + OOB stats strip and trigger modal close + toast."""
    context = _get_user_library_context(request.user)
    grid_html = render_to_string('library/partials/entry_grid.html', context, request=request)
    stats_html = render_to_string(
        'library/partials/stats_strip.html',
        {**context, 'oob': True},
        request=request,
    )
    response = HttpResponse(grid_html + stats_html)
    response['HX-Trigger'] = json.dumps({
        'closeModal': True,
        'show-toast': {'message': toast_message, 'level': level},
    })
    return response


class GrandLibraryView(LoginRequiredMixin, ListView):
    """Render the authenticated user's Grand Library visual grid dashboard."""

    model = LibraryEntry
    template_name = 'library/dashboard.html'
    context_object_name = 'entries'

    def get_queryset(self):
        return (
            LibraryEntry.objects.filter(user=self.request.user)
            .select_related('folder')
            .prefetch_related('tags')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_get_user_library_context(self.request.user))
        context['entries'] = self.object_list
        return context


class LibraryEntryCreateView(LoginRequiredMixin, CreateView):
    """Create a new LibraryEntry with custom alias/cover overrides via HTMX modal or page."""

    model = LibraryEntry
    form_class = LibraryEntryForm
    success_url = reverse_lazy('library:dashboard')

    def get_template_names(self):
        if self.request.htmx:
            return ['library/partials/entry_form_modal.html']
        return ['library/entry_form_page.html']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = 'Add Story to Grand Library'
        context['submit_label'] = 'Save Story'
        context['form_action'] = reverse_lazy('library:entry_create')
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        ReadingSnapshot.objects.create(
            entry=self.object,
            uri=self.object.current_uri,
            chapter_label=self.object.chapter_label,
            notes=self.object.notes,
        )
        if self.request.htmx:
            return _render_htmx_grid_response(
                self.request,
                f'Added "{self.object.custom_title}" to your Grand Library.',
            )
        messages.success(self.request, f'Added "{self.object.custom_title}" to your Grand Library.')
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            response['HX-Retarget'] = '#modal-dialog-body'
            response['HX-Reswap'] = 'innerHTML'
        return response


class LibraryEntryUpdateView(LoginRequiredMixin, UpdateView):
    """Edit metadata overrides, custom cover art, and taxonomy for a user-owned LibraryEntry."""

    model = LibraryEntry
    form_class = LibraryEntryForm
    success_url = reverse_lazy('library:dashboard')

    def get_queryset(self):
        return LibraryEntry.objects.filter(user=self.request.user)

    def get_template_names(self):
        if self.request.htmx:
            return ['library/partials/entry_form_modal.html']
        return ['library/entry_form_page.html']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = f'Customize "{self.object.custom_title}"'
        context['submit_label'] = 'Save Changes'
        context['form_action'] = reverse_lazy('library:entry_update', kwargs={'pk': self.object.pk})
        return context

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return _render_htmx_grid_response(
                self.request,
                f'Updated "{self.object.custom_title}".',
            )
        messages.success(self.request, f'Updated "{self.object.custom_title}".')
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            response['HX-Retarget'] = '#modal-dialog-body'
            response['HX-Reswap'] = 'innerHTML'
        return response


class LibraryEntryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a user-owned LibraryEntry via HTMX confirmation modal or standard POST."""

    model = LibraryEntry
    success_url = reverse_lazy('library:dashboard')

    def get_queryset(self):
        return LibraryEntry.objects.filter(user=self.request.user)

    def get_template_names(self):
        if self.request.htmx:
            return ['library/partials/entry_delete_modal.html']
        return ['library/entry_delete_page.html']

    def form_valid(self, form):
        title = self.object.custom_title
        self.object.delete()
        if self.request.htmx:
            return _render_htmx_grid_response(
                self.request,
                f'Removed "{title}" from your Grand Library.',
                level='info',
            )
        messages.info(self.request, f'Removed "{title}" from your Grand Library.')
        return HttpResponse(status=302, headers={'Location': str(self.success_url)})


def home_view(request):
    """Render the Grand Library for authenticated users or the landing shell for guests."""
    if request.user.is_authenticated:
        return GrandLibraryView.as_view()(request)
    return render(request, 'library/home.html')
