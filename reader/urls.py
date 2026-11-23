from django.urls import path

from .views import ViewportReaderView

app_name = 'reader'

urlpatterns = [
    path('<uuid:entry_id>/', ViewportReaderView.as_view(), name='viewport'),
]
