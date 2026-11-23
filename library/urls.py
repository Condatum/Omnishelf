from django.urls import path

from .views import (
    GrandLibraryView,
    LibraryEntryCreateView,
    LibraryEntryDeleteView,
    LibraryEntryUpdateView,
    folder_create_view,
    folder_delete_view,
    folder_rename_view,
    omni_search_view,
    tag_create_view,
    tag_delete_view,
    tag_rename_view,
)

app_name = 'library'

urlpatterns = [
    path('', GrandLibraryView.as_view(), name='dashboard'),
    path('search/', omni_search_view, name='omni_search'),
    path('entries/new/', LibraryEntryCreateView.as_view(), name='entry_create'),
    path('entries/<uuid:pk>/edit/', LibraryEntryUpdateView.as_view(), name='entry_update'),
    path('entries/<uuid:pk>/delete/', LibraryEntryDeleteView.as_view(), name='entry_delete'),
    # Dynamic Taxonomy CRUD endpoints
    path('folders/new/', folder_create_view, name='folder_create'),
    path('folders/<uuid:pk>/rename/', folder_rename_view, name='folder_rename'),
    path('folders/<uuid:pk>/delete/', folder_delete_view, name='folder_delete'),
    path('tags/new/', tag_create_view, name='tag_create'),
    path('tags/<uuid:pk>/rename/', tag_rename_view, name='tag_rename'),
    path('tags/<uuid:pk>/delete/', tag_delete_view, name='tag_delete'),
]
