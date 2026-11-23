import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import FolderForm, LibraryEntryForm, TagForm
from .models import Folder, LibraryEntry, ReadingSnapshot, ReadingStatus, Tag


def _extract_filter_params(request) -> dict:
    """Read active status, folder, tag, and Omni-Search query parameters."""
    source = request.GET if request.method == 'GET' else request.POST
    status = (source.get('status') or '').strip().upper()
    if status not in ReadingStatus.values:
        status = ''

    folder_param = (source.get('folder') or '').strip()
    tag_slug = (source.get('tag') or '').strip()
    query = (source.get('q') or '').strip()
    return {
        'active_status': status,
        'active_folder': folder_param,
        'active_tag': tag_slug,
        'active_query': query,
    }


def _get_user_library_context(user, filters: dict | None = None) -> dict:
    """Build strictly user-scoped filtered entries, Omni-Search matches, sidebar data, and stats."""
    filters = filters or {}
    active_status = filters.get('active_status', '')
    active_folder = filters.get('active_folder', '')
    active_tag = filters.get('active_tag', '')
    active_query = (filters.get('active_query') or '').strip()

    base_qs = LibraryEntry.objects.filter(user=user)
    entries = base_qs.select_related('folder').prefetch_related('tags')

    active_folder_obj = None
    active_tag_obj = None

    if active_status in ReadingStatus.values:
        entries = entries.filter(status=active_status)

    if active_folder == 'unfiled':
        entries = entries.filter(folder__isnull=True)
    elif active_folder:
        try:
            folder_uuid = uuid.UUID(str(active_folder))
            active_folder_obj = Folder.objects.filter(user=user, pk=folder_uuid).first()
            if active_folder_obj:
                entries = entries.filter(folder=active_folder_obj)
            else:
                active_folder = ''
        except ValueError:
            active_folder = ''

    if active_tag:
        active_tag_obj = Tag.objects.filter(user=user, slug=active_tag).first()
        if active_tag_obj:
            entries = entries.filter(tags=active_tag_obj)
        else:
            active_tag = ''

    if active_query:
        for term in active_query.split():
            entries = entries.filter(
                Q(custom_title__icontains=term)
                | Q(original_source_title__icontains=term)
                | Q(tags__name__icontains=term)
                | Q(source_domain__icontains=term)
                | Q(notes__icontains=term)
            )

    entries = entries.distinct()

    stats = base_qs.aggregate(
        total_count=Count('id'),
        active_count=Count('id', filter=Q(status=ReadingStatus.ACTIVE)),
        binge_ready_count=Count('id', filter=Q(status=ReadingStatus.BINGE_READY)),
        on_hold_count=Count('id', filter=Q(status=ReadingStatus.ON_HOLD)),
        hiatus_count=Count('id', filter=Q(status=ReadingStatus.HIATUS)),
        completed_count=Count('id', filter=Q(status=ReadingStatus.COMPLETED)),
        unfiled_count=Count('id', filter=Q(folder__isnull=True)),
    )

    folders = Folder.objects.filter(user=user).annotate(
        entry_count=Count('entries', filter=Q(entries__user=user), distinct=True),
    )
    tags = Tag.objects.filter(user=user).annotate(
        entry_count=Count('entries', filter=Q(entries__user=user), distinct=True),
    )

    status_tabs = [
        {'value': '', 'label': 'All', 'count': stats['total_count']},
        {'value': ReadingStatus.ACTIVE, 'label': 'Active', 'count': stats['active_count']},
        {'value': ReadingStatus.BINGE_READY, 'label': 'Binge-Ready', 'count': stats['binge_ready_count']},
        {'value': ReadingStatus.ON_HOLD, 'label': 'On Hold', 'count': stats['on_hold_count']},
        {'value': ReadingStatus.HIATUS, 'label': 'Hiatus', 'count': stats['hiatus_count']},
        {'value': ReadingStatus.COMPLETED, 'label': 'Completed', 'count': stats['completed_count']},
    ]

    has_active_filters = bool(active_status or active_folder or active_tag or active_query)

    return {
        'entries': entries,
        **stats,
        'folders': folders,
        'tags': tags,
        'status_choices': ReadingStatus.choices,
        'status_tabs': status_tabs,
        'active_status': active_status,
        'active_folder': active_folder,
        'active_folder_obj': active_folder_obj,
        'active_tag': active_tag,
        'active_tag_obj': active_tag_obj,
        'active_query': active_query,
        'has_active_filters': has_active_filters,
    }


def _render_htmx_filter_fragments(request, context) -> HttpResponse:
    """Return grid HTML plus OOB status tabs, taxonomy sidebar, and search hidden filter state."""
    grid_html = render_to_string('library/partials/entry_grid.html', context, request=request)
    tabs_html = render_to_string(
        'library/partials/status_tabs.html',
        {**context, 'oob': True},
        request=request,
    )
    sidebar_html = render_to_string(
        'library/partials/taxonomy_sidebar.html',
        {**context, 'oob': True},
        request=request,
    )
    hidden_filters_html = render_to_string(
        'library/partials/omni_search_hidden_filters.html',
        {**context, 'oob': True},
        request=request,
    )
    return HttpResponse(grid_html + tabs_html + sidebar_html + hidden_filters_html)


def _render_htmx_workspace_response(
    request,
    toast_message: str,
    level: str = 'success',
    close_modal: bool = True,
    filters: dict | None = None,
) -> HttpResponse:
    """Return updated entry grid + OOB stats strip + OOB sidebar + status tabs."""
    context = _get_user_library_context(request.user, filters=filters)
    grid_html = render_to_string('library/partials/entry_grid.html', context, request=request)
    stats_html = render_to_string(
        'library/partials/stats_strip.html',
        {**context, 'oob': True},
        request=request,
    )
    sidebar_html = render_to_string(
        'library/partials/taxonomy_sidebar.html',
        {**context, 'oob': True},
        request=request,
    )
    tabs_html = render_to_string(
        'library/partials/status_tabs.html',
        {**context, 'oob': True},
        request=request,
    )
    response = HttpResponse(grid_html + stats_html + sidebar_html + tabs_html)
    trigger_payload = {'show-toast': {'message': toast_message, 'level': level}}
    if close_modal:
        trigger_payload['closeModal'] = True
    response['HX-Trigger'] = json.dumps(trigger_payload)
    return response


class GrandLibraryView(LoginRequiredMixin, ListView):
    """Render the authenticated user's Grand Library with dynamic taxonomy & Omni-Search filtering."""

    model = LibraryEntry
    template_name = 'library/dashboard.html'
    context_object_name = 'entries'

    def get_queryset(self):
        self._filters = _extract_filter_params(self.request)
        self._library_context = _get_user_library_context(self.request.user, filters=self._filters)
        return self._library_context['entries']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self._library_context)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            return _render_htmx_filter_fragments(self.request, context)
        return super().render_to_response(context, **response_kwargs)


@login_required
def omni_search_view(request):
    """Real-time HTMX Omni-Search endpoint combining query text with Folder/Tag/Status filters."""
    filters = _extract_filter_params(request)
    context = _get_user_library_context(request.user, filters=filters)
    if request.htmx:
        return _render_htmx_filter_fragments(request, context)
    return render(request, 'library/dashboard.html', context)


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
            return _render_htmx_workspace_response(
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
            return _render_htmx_workspace_response(
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
            return _render_htmx_workspace_response(
                self.request,
                f'Removed "{title}" from your Grand Library.',
                level='info',
            )
        messages.info(self.request, f'Removed "{title}" from your Grand Library.')
        return HttpResponse(status=302, headers={'Location': str(self.success_url)})


def _render_sidebar_htmx_response(request, toast_message: str, level: str = 'success', refresh_grid: bool = False):
    """Return updated sidebar partial and optionally OOB-refresh the story grid."""
    context = _get_user_library_context(request.user)
    sidebar_html = render_to_string('library/partials/taxonomy_sidebar.html', context, request=request)
    if refresh_grid:
        grid_html = render_to_string(
            'library/partials/entry_grid.html',
            {**context, 'oob': True},
            request=request,
        )
        body = sidebar_html + grid_html
    else:
        body = sidebar_html
    response = HttpResponse(body)
    response['HX-Trigger'] = json.dumps({
        'show-toast': {'message': toast_message, 'level': level},
    })
    return response


@login_required
@require_POST
def folder_create_view(request):
    """Create a user-scoped Folder from the taxonomy sidebar."""
    form = FolderForm(request.POST, user=request.user)
    if form.is_valid():
        folder = form.save(commit=False)
        folder.user = request.user
        folder.save()
        if request.htmx:
            return _render_sidebar_htmx_response(request, f'Created folder "{folder.name}".')
        messages.success(request, f'Created folder "{folder.name}".')
    else:
        err = next(iter(form.errors.values()))[0]
        if request.htmx:
            return _render_sidebar_htmx_response(request, str(err), level='error')
        messages.error(request, str(err))
    return redirect('library:dashboard')


@login_required
@require_POST
def folder_rename_view(request, pk):
    """Rename a user-owned Folder inline from the taxonomy sidebar."""
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    form = FolderForm(request.POST, instance=folder, user=request.user)
    if form.is_valid():
        folder = form.save()
        if request.htmx:
            return _render_sidebar_htmx_response(
                request,
                f'Renamed folder to "{folder.name}".',
                refresh_grid=True,
            )
        messages.success(request, f'Renamed folder to "{folder.name}".')
    else:
        err = next(iter(form.errors.values()))[0]
        if request.htmx:
            return _render_sidebar_htmx_response(request, str(err), level='error')
        messages.error(request, str(err))
    return redirect('library:dashboard')


@login_required
@require_POST
def folder_delete_view(request, pk):
    """Delete a user-owned Folder (preserving its stories as unfiled)."""
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    name = folder.name
    folder.delete()
    if request.htmx:
        return _render_sidebar_htmx_response(
            request,
            f'Deleted folder "{name}".',
            level='info',
            refresh_grid=True,
        )
    messages.info(request, f'Deleted folder "{name}".')
    return redirect('library:dashboard')


@login_required
@require_POST
def tag_create_view(request):
    """Create a user-scoped Tag from the taxonomy sidebar."""
    form = TagForm(request.POST, user=request.user)
    if form.is_valid():
        tag = form.save(commit=False)
        tag.user = request.user
        tag.slug = slugify(tag.name)
        tag.save()
        if request.htmx:
            return _render_sidebar_htmx_response(request, f'Created tag "#{tag.name}".')
        messages.success(request, f'Created tag "#{tag.name}".')
    else:
        err = next(iter(form.errors.values()))[0]
        if request.htmx:
            return _render_sidebar_htmx_response(request, str(err), level='error')
        messages.error(request, str(err))
    return redirect('library:dashboard')


@login_required
@require_POST
def tag_rename_view(request, pk):
    """Rename a user-owned Tag and update its slug cleanly."""
    tag = get_object_or_404(Tag, pk=pk, user=request.user)
    form = TagForm(request.POST, instance=tag, user=request.user)
    if form.is_valid():
        tag = form.save(commit=False)
        tag.slug = slugify(tag.name)
        tag.save()
        if request.htmx:
            return _render_sidebar_htmx_response(
                request,
                f'Renamed tag to "#{tag.name}".',
                refresh_grid=True,
            )
        messages.success(request, f'Renamed tag to "#{tag.name}".')
    else:
        err = next(iter(form.errors.values()))[0]
        if request.htmx:
            return _render_sidebar_htmx_response(request, str(err), level='error')
        messages.error(request, str(err))
    return redirect('library:dashboard')


@login_required
@require_POST
def tag_delete_view(request, pk):
    """Delete a user-owned Tag from the taxonomy sidebar."""
    tag = get_object_or_404(Tag, pk=pk, user=request.user)
    name = tag.name
    tag.delete()
    if request.htmx:
        return _render_sidebar_htmx_response(
            request,
            f'Deleted tag "#{name}".',
            level='info',
            refresh_grid=True,
        )
    messages.info(request, f'Deleted tag "#{name}".')
    return redirect('library:dashboard')


def home_view(request):
    """Render the Grand Library for authenticated users or the landing shell for guests."""
    if request.user.is_authenticated:
        return GrandLibraryView.as_view()(request)
    return render(request, 'library/home.html')
