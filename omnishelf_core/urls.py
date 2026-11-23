from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from library.views import (
    home_view,
    track_resume_latency_view,
    usability_feedback_view,
    ux_metrics_dashboard_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('library/', include('library.urls')),
    path('reader/', include('reader.urls')),
    path('ux-metrics/', ux_metrics_dashboard_view, name='ux_metrics'),
    path('ux-metrics/feedback/', usability_feedback_view, name='usability_feedback'),
    path('ux-metrics/track-resume/', track_resume_latency_view, name='track_resume_latency'),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
