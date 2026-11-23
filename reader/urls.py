from django.urls import path

from .views import (
    ViewportReaderView,
    freeze_snapshot_view,
    quick_snapshot_modal_view,
    rollback_snapshot_view,
)

app_name = 'reader'

urlpatterns = [
    path('<uuid:entry_id>/', ViewportReaderView.as_view(), name='viewport'),
    path('<uuid:entry_id>/quick-snapshot/', quick_snapshot_modal_view, name='quick_snapshot_modal'),
    path('<uuid:entry_id>/freeze/', freeze_snapshot_view, name='freeze_snapshot'),
    path('<uuid:entry_id>/rollback/<uuid:snapshot_id>/', rollback_snapshot_view, name='rollback_snapshot'),
]
