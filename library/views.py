from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import ListView

from .models import Folder, LibraryEntry, ReadingStatus, Tag


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
        base_qs = LibraryEntry.objects.filter(user=self.request.user)
        stats = base_qs.aggregate(
            total_count=Count('id'),
            active_count=Count('id', filter=Q(status=ReadingStatus.ACTIVE)),
            binge_ready_count=Count('id', filter=Q(status=ReadingStatus.BINGE_READY)),
            on_hold_count=Count('id', filter=Q(status=ReadingStatus.ON_HOLD)),
            hiatus_count=Count('id', filter=Q(status=ReadingStatus.HIATUS)),
            completed_count=Count('id', filter=Q(status=ReadingStatus.COMPLETED)),
        )
        context.update(stats)
        context['folders'] = Folder.objects.filter(user=self.request.user)
        context['tags'] = Tag.objects.filter(user=self.request.user)
        context['status_choices'] = ReadingStatus.choices
        return context


def home_view(request):
    """Render the Grand Library for authenticated users or the landing shell for guests."""
    if request.user.is_authenticated:
        return GrandLibraryView.as_view()(request)
    return render(request, 'library/home.html')
