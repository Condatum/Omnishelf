from django.urls import path

from .views import (
    GrandLibraryView,
    LibraryEntryCreateView,
    LibraryEntryDeleteView,
    LibraryEntryUpdateView,
)

app_name = 'library'

urlpatterns = [
    path('', GrandLibraryView.as_view(), name='dashboard'),
    path('entries/new/', LibraryEntryCreateView.as_view(), name='entry_create'),
    path('entries/<uuid:pk>/edit/', LibraryEntryUpdateView.as_view(), name='entry_update'),
    path('entries/<uuid:pk>/delete/', LibraryEntryDeleteView.as_view(), name='entry_delete'),
]
