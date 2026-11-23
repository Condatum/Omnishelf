import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import FolderForm, LibraryEntryForm, TagForm, UsabilityFeedbackForm
from .models import Folder, LibraryEntry, ReadingSnapshot, ReadingStatus, Tag, UsabilityMetric, UtilityRating


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


MANUAL_BASELINE_RESUME_SECONDS = 45.0


def _compute_ux_metrics_summary(user) -> dict:
    """Compute anonymized study cohort aggregates alongside strictly user-scoped personal telemetry."""
    rated_qs = UsabilityMetric.objects.exclude(utility_rating='')
    rating_agg = rated_qs.aggregate(
        total_ratings=Count('id'),
        high_count=Count('id', filter=Q(utility_rating=UtilityRating.HIGH)),
        moderate_count=Count('id', filter=Q(utility_rating=UtilityRating.MODERATE)),
        low_count=Count('id', filter=Q(utility_rating=UtilityRating.LOW)),
        participant_count=Count('user', distinct=True),
    )
    total_ratings = rating_agg['total_ratings'] or 0
    high_count = rating_agg['high_count'] or 0
    moderate_count = rating_agg['moderate_count'] or 0
    low_count = rating_agg['low_count'] or 0
    high_utility_pct = round((high_count / total_ratings) * 100, 1) if total_ratings else 0.0
    moderate_pct = round((moderate_count / total_ratings) * 100, 1) if total_ratings else 0.0
    low_pct = round((low_count / total_ratings) * 100, 1) if total_ratings else 0.0

    latency_agg = UsabilityMetric.objects.filter(
        session_start_to_resume_ms__isnull=False,
    ).aggregate(
        avg_ms=Avg('session_start_to_resume_ms'),
        session_count=Count('id'),
    )
    avg_resume_ms = round(latency_agg['avg_ms']) if latency_agg['avg_ms'] is not None else None
    avg_resume_seconds = round(avg_resume_ms / 1000.0, 2) if avg_resume_ms is not None else None
    time_saved_seconds = (
        round(max(0.0, MANUAL_BASELINE_RESUME_SECONDS - avg_resume_seconds), 2)
        if avg_resume_seconds is not None
        else None
    )

    # Strictly user-scoped personal telemetry records (never leaks another user's notes or entries)
    personal_qs = UsabilityMetric.objects.filter(user=user).select_related('entry')
    personal_latency = personal_qs.filter(session_start_to_resume_ms__isnull=False).aggregate(
        avg_ms=Avg('session_start_to_resume_ms'),
        count=Count('id'),
    )
    personal_avg_seconds = (
        round(personal_latency['avg_ms'] / 1000.0, 2)
        if personal_latency['avg_ms'] is not None
        else None
    )

    return {
        'cohort_total_ratings': total_ratings,
        'cohort_high_count': high_count,
        'cohort_moderate_count': moderate_count,
        'cohort_low_count': low_count,
        'cohort_high_utility_pct': high_utility_pct,
        'cohort_moderate_pct': moderate_pct,
        'cohort_low_pct': low_pct,
        'cohort_meets_target': total_ratings > 0 and high_utility_pct >= 60.0,
        'cohort_participant_count': rating_agg['participant_count'] or 0,
        'cohort_avg_resume_ms': avg_resume_ms,
        'cohort_avg_resume_seconds': avg_resume_seconds,
        'cohort_session_count': latency_agg['session_count'] or 0,
        'cohort_time_saved_seconds': time_saved_seconds,
        'manual_baseline_seconds': MANUAL_BASELINE_RESUME_SECONDS,
        'personal_metrics': personal_qs[:20],
        'personal_avg_seconds': personal_avg_seconds,
        'personal_session_count': personal_latency['count'] or 0,
    }


@login_required
def ux_metrics_dashboard_view(request):
    """Display session-start latency savings and live High Utility usability study metrics."""
    context = _compute_ux_metrics_summary(request.user)
    return render(request, 'library/ux_metrics.html', context)


@login_required
@require_POST
def track_resume_latency_view(request):
    """Record elapsed milliseconds from dashboard load to clicking Deep-Link Resume."""
    raw_ms = request.POST.get('session_start_to_resume_ms')
    entry_id = request.POST.get('entry_id')

    if raw_ms is None and request.body:
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            raw_ms = body_data.get('session_start_to_resume_ms')
            entry_id = body_data.get('entry_id')
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid payload'}, status=400)

    try:
        elapsed_ms = int(round(float(raw_ms)))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid session_start_to_resume_ms value'}, status=400)

    elapsed_ms = max(0, min(elapsed_ms, 600_000))

    entry = None
    if entry_id:
        try:
            entry_uuid = uuid.UUID(str(entry_id))
            entry = LibraryEntry.objects.filter(user=request.user, pk=entry_uuid).first()
        except ValueError:
            entry = None

    metric = UsabilityMetric.objects.create(
        user=request.user,
        entry=entry,
        session_start_to_resume_ms=elapsed_ms,
    )
    return JsonResponse({
        'id': str(metric.pk),
        'session_start_to_resume_ms': metric.session_start_to_resume_ms,
    }, status=201)


@login_required
def usability_feedback_view(request):
    """Render and process the Usability Study Feedback Modal (High/Moderate/Low Utility)."""
    if request.method == 'POST':
        form = UsabilityFeedbackForm(request.POST)
        if form.is_valid():
            metric = form.save(commit=False)
            metric.user = request.user
            raw_ms = request.POST.get('session_start_to_resume_ms')
            if raw_ms:
                try:
                    metric.session_start_to_resume_ms = max(0, min(int(round(float(raw_ms))), 600_000))
                except ValueError:
                    pass
            metric.save()
            if request.htmx:
                if request.POST.get('from_metrics_page') == '1':
                    context = _compute_ux_metrics_summary(request.user)
                    html = render_to_string(
                        'library/partials/ux_metrics_summary.html',
                        context,
                        request=request,
                    )
                    response = HttpResponse(html)
                else:
                    response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({
                    'closeModal': True,
                    'show-toast': {
                        'message': f'Thank you! Recorded "{metric.get_utility_rating_display()}" usability feedback.',
                        'level': 'success',
                    },
                })
                return response
            messages.success(
                request,
                f'Thank you! Recorded "{metric.get_utility_rating_display()}" usability feedback.',
            )
            return redirect('ux_metrics')
    else:
        form = UsabilityFeedbackForm()

    context = {
        'form': form,
        'from_metrics_page': request.GET.get('from_metrics_page') == '1',
    }
    if request.htmx:
        return render(request, 'library/partials/usability_feedback_modal.html', context)
    return render(request, 'library/usability_feedback_page.html', context)


def home_view(request):
    """Render the Grand Library for authenticated users or the landing shell for guests."""
    if request.user.is_authenticated:
        return GrandLibraryView.as_view()(request)
    return render(request, 'library/home.html')
