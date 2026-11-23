from django.urls import path

from .views import GrandLibraryView

app_name = 'library'

urlpatterns = [
    path('', GrandLibraryView.as_view(), name='dashboard'),
]
